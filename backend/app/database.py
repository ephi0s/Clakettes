"""Database engine, session factory, and base model registry.

Supports both SQLite (development) and MariaDB (production) backends.
Configures connection pooling appropriate for each backend.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = connect_args
    if ":memory:" in settings.DATABASE_URL:
        engine_args["poolclass"] = StaticPool
    else:
        engine_args["poolclass"] = NullPool
else:
    # MariaDB/MySQL: Connection pool for concurrent requests
    engine_args["pool_size"] = 10  # Persistent connections
    engine_args["max_overflow"] = 20  # Additional connections under load
    engine_args["pool_pre_ping"] = True  # Verify connection before use
    engine_args["pool_recycle"] = 3600  # Recycle connections hourly

engine = create_engine(settings.DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session.

    Usage:
        @app.get("/items/")
        async def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Behavior:
    - Creates new session per request
    - Rolls back on exception
    - Always closes session in finally block
    - Works with both sync and async endpoints (SQLAlchemy 2.0)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
