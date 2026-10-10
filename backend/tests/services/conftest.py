"""Shared fixtures for service-layer unit tests."""

import os

os.environ["TESTING"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.services.user_service import hash_password

from app.models.base import Base
from app.models.festival import Festival
from app.models.user import User
from app.models.shortfilm import ShortFilm
from app.models.role import Role
from app.models.registration import (
    RegistrationForm,
)
from app.models.event import (
    Event,
)

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def create_user(db_session):
    """Factory fixture: create a user and return it."""

    def _create(username="testuser", email="test@example.com", role="user", password="Test1234"):
        user = User(
            username=username,
            email=email,
            full_name="Test User",
            role=role,
            password_hash=hash_password(password),
            is_active=True,
            is_public=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create


@pytest.fixture
def create_festival(db_session):
    """Factory fixture: create a festival and return it."""

    def _create(name="Test Festival", location="Test City"):
        festival = Festival(name=name, location=location, is_active=True)
        db_session.add(festival)
        db_session.commit()
        db_session.refresh(festival)
        return festival

    return _create


@pytest.fixture
def create_shortfilm(db_session, create_user, create_festival):
    """Factory fixture: create a short film and return it."""

    def _create(title="Test Film", festival_id=None, user_id=None, is_public=True):
        if festival_id is None:
            festival = create_festival()
            festival_id = festival.id
        if user_id is None:
            user = create_user()
            user_id = user.id
        film = ShortFilm(
            title=title,
            description="A test short film",
            duration=120,
            festival_id=festival_id,
            user_id=user_id,
            is_public=is_public,
        )
        db_session.add(film)
        db_session.commit()
        db_session.refresh(film)
        return film

    return _create


@pytest.fixture
def create_role(db_session):
    """Factory fixture: create a role and return it."""

    def _create(name="test_role", display_name="Test Role", hierarchy_level=50, scope="global"):
        from app.models.role import RoleScope

        role = Role(
            name=name,
            display_name=display_name,
            hierarchy_level=hierarchy_level,
            scope=RoleScope(scope),
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        return role

    return _create


@pytest.fixture
def create_registration_form(db_session, create_festival):
    """Factory fixture: create a registration form for a festival."""

    def _create(festival_id=None, is_active=True, max_registrations=None):
        if festival_id is None:
            festival = create_festival()
            festival_id = festival.id
        form = RegistrationForm(
            festival_id=festival_id,
            title="Test Form",
            description="A test form",
            is_active=is_active,
            max_registrations=max_registrations,
        )
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        return form

    return _create


@pytest.fixture
def create_event(db_session, create_festival):
    """Factory fixture: create an event for a festival."""

    def _create(festival_id=None, event_type="screening", is_active=True):
        if festival_id is None:
            festival = create_festival()
            festival_id = festival.id
        from datetime import datetime

        event = Event(
            festival_id=festival_id,
            title="Test Event",
            event_type=event_type,
            start_date=datetime(2026, 7, 1),
            end_date=datetime(2026, 7, 2),
            is_active=is_active,
            is_public=True,
            location="Test Venue",
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        return event

    return _create
