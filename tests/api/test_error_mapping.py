"""HTTP-seam tests: domain errors map to the exact status + body the GUI relies on.

These cross the real HTTP seam (auth, status mapping, ``{"detail": ...}`` shape).
They are the regression guard for "responses stay identical" — the GUI branches on
``status_code == 404`` and reads ``body["detail"]``.
"""

from collections.abc import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.backend.core.config import config as cfg
from src.backend.db.database import get_db
from src.backend.main import app

HEADERS = {"x-api-key": cfg.api_key}


@pytest.fixture
def client() -> Generator[TestClient]:
    """Yield a TestClient backed by an isolated in-memory DB (no app lifespan)."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def override_get_db() -> Generator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    # No `with TestClient(...)`: skipping the lifespan keeps startup migrations and
    # the backup task away from the real database path.
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create(client: TestClient, nfc_id: str, *, is_adult: bool = True, balance: float = 0) -> None:
    resp = client.post(
        "/api/users",
        json={"nfc_id": nfc_id, "is_adult": is_adult, "balance": balance},
        headers=HEADERS,
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_missing_api_key_is_401(client: TestClient) -> None:
    resp = client.get("/api/users/ANY")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Missing API Key"}


def test_user_not_found_is_404(client: TestClient) -> None:
    resp = client.get("/api/users/NOPE", headers=HEADERS)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "User not found"}


def test_duplicate_nfc_is_400(client: TestClient) -> None:
    _create(client, "DUP")
    resp = client.post(
        "/api/users", json={"nfc_id": "DUP", "is_adult": True, "balance": 0}, headers=HEADERS
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "User with NFC ID DUP already exists"}


def test_insufficient_balance_is_402(client: TestClient) -> None:
    _create(client, "POOR", balance=5)
    resp = client.post(
        "/api/users/POOR/cocktails/book",
        json={"name": "Mojito", "price": 10, "is_alcoholic": False},
        headers=HEADERS,
    )
    assert resp.status_code == status.HTTP_402_PAYMENT_REQUIRED
    assert resp.json() == {"detail": "Insufficient balance. Current: 5.00, Required: 10.00"}


def test_underage_booking_is_403(client: TestClient) -> None:
    _create(client, "KID", is_adult=False, balance=50)
    resp = client.post(
        "/api/users/KID/cocktails/book",
        json={"name": "Beer", "price": 5, "is_alcoholic": True},
        headers=HEADERS,
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.json() == {"detail": "User is underage and cannot purchase alcoholic cocktails"}


def test_balance_below_minimum_is_400(client: TestClient) -> None:
    _create(client, "ACC", balance=10)
    resp = client.post("/api/users/ACC/balance/top-up", json={"amount": -50}, headers=HEADERS)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Balance cannot go below €0.00. Current: 10.00, Requested: -50.00"}
