"""Pytest configuration and shared fixtures."""

from collections.abc import Generator
from typing import Any

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.backend.models.user import User
from src.backend.service.user_service import UserService


@pytest.fixture(scope="function")
def db_engine() -> Generator[Any, None, None]:
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: Any) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def user_service(db_session: Session) -> UserService:
    """Create a UserService with the test database session."""
    return UserService(db_session)


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(nfc_id="TEST123", balance=50.0, is_adult=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_minor(db_session: Session) -> User:
    """Create a sample minor user for testing."""
    user = User(nfc_id="MINOR456", balance=30.0, is_adult=False)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
