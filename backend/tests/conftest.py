"""Shared fixtures for all backend tests."""

import os
import atexit
import tempfile

# Set up test environment BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["APP_ENV"] = "testing"

# Use shared in-memory SQLite for consistent behavior across test connections
TEST_SQLITE_URL = "sqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_SQLITE_URL

# Create temporary rate limit database
_rate_limits_fd, _rate_limits_path = tempfile.mkstemp(suffix=".db")
os.close(_rate_limits_fd)
os.environ["RATE_LIMITS_DB_PATH"] = _rate_limits_path


def _cleanup_rate_limits_db() -> None:
    try:
        os.remove(_rate_limits_path)
    except OSError:
        pass


atexit.register(_cleanup_rate_limits_db)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import database as app_database  # noqa: E402
from app.database import get_db  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.services.user_service import UserService  # noqa: E402

# -- Bcrypt speed-up -----------------------------------------------------------
# Default bcrypt cost (12 rounds, ~220ms/hash) slows down every user-creating test.
# We swap hash/verify for 4-round versions. bcrypt.checkpw reads the rounds from
# the stored hash, so verification of these fast hashes still works.


@pytest.fixture(scope="session", autouse=True)
def fast_bcrypt():
    import bcrypt
    import app.services.user_service as user_service
    import app.main as app_main
    import app.routers.admin as admin_router

    def _hash(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=4)).decode("utf-8")

    def _verify(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    orig_hash = user_service.hash_password
    orig_verify = user_service.verify_password
    user_service.hash_password = _hash
    user_service.verify_password = _verify
    # Modules that did `from app.services.user_service import hash/verify_password`
    # have bound the function into their own namespace; patch those copies too.
    app_main.hash_password = _hash
    admin_router.verify_password = _verify
    services_conftest = None
    orig_services_hash = None
    try:
        import tests.services.conftest as services_conftest
    except Exception:
        services_conftest = None
    if services_conftest is not None:
        orig_services_hash = services_conftest.hash_password
        services_conftest.hash_password = _hash
    yield
    user_service.hash_password = orig_hash
    user_service.verify_password = orig_verify
    if services_conftest is not None:
        services_conftest.hash_password = orig_services_hash


# -- Database ------------------------------------------------------------------

TEST_DATABASE_URL = TEST_SQLITE_URL

# Single shared engine for in-memory SQLite
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Point app's engine/session to use the same test engine/session
app_database.engine = engine
app_database.SessionLocal = TestingSessionLocal

Base.metadata.create_all(bind=engine)


def _truncate_all():
    """Delete every row from all tables in reverse FK-dependency order.

    The schema is created once at import; per-test isolation is achieved by
    emptying the tables (SQLite rowids restart at 1 on a full delete).
    """
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture(scope="function")
def db_session():
    """Yield a session; teardown rolls back and empties all tables."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        _truncate_all()


# -- Client --------------------------------------------------------------------


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_databases():
    yield
    # Clean up temporary databases after tests complete
    try:
        if os.path.exists(_rate_limits_path):
            os.remove(_rate_limits_path)
    except Exception:
        pass


# -- Auth helpers --------------------------------------------------------------


@pytest.fixture
def user_service():
    return UserService()


@pytest.fixture
def create_user(db_session):
    """Factory fixture: create a user and return (user, plain_password)."""

    def _create(username="testuser", email="test@example.com", role="user", password="Test1234"):
        svc = UserService()
        from app.schemas.user import UserCreate

        user = svc.create(
            db_session,
            UserCreate(
                username=username,
                email=email,
                full_name="Test User",
                role=role,
                password=password,
            ),
        )
        return user, password

    return _create


@pytest.fixture
def auth_headers(create_user, db_session):
    """Return Authorization headers for an authenticated user."""
    from app.auth import create_session

    user, password = create_user()
    session, access_token, _ = create_session(db_session, user.id)
    return {"Authorization": f"Bearer {access_token}"}, user


@pytest.fixture
def admin_headers(create_user, db_session):
    """Return Authorization headers for an admin user."""
    from app.auth import create_session

    user, password = create_user(username="admin", email="admin@example.com", role="admin")
    session, access_token, _ = create_session(db_session, user.id)
    return {"Authorization": f"Bearer {access_token}"}, user
