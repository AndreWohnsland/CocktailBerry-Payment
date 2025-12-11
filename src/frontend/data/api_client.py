from typing import Any

import requests

from ..constants import HTTP_CREATED, HTTP_NO_CONTENT, HTTP_OK

API_URL = "http://localhost:8000"


def get_user(nfc_id: str) -> dict[str, Any] | None:
    """Get user by NFC ID."""
    try:
        response = requests.get(f"{API_URL}/api/users/{nfc_id}", timeout=2)
        if response.status_code == HTTP_OK:
            return response.json()
    except Exception:
        pass
    return None


def list_users() -> list[dict[str, Any]]:
    """List all users."""
    try:
        response = requests.get(f"{API_URL}/api/users", timeout=2)
        if response.status_code == HTTP_OK:
            return response.json()
    except Exception:
        pass
    return []


def create_user(nfc_id: str, is_adult: bool) -> dict[str, Any] | None:
    """Create a new user."""
    try:
        response = requests.post(
            f"{API_URL}/api/users",
            json={"nfc_id": nfc_id, "is_adult": is_adult},
            timeout=2,
        )
        if response.status_code == HTTP_CREATED:
            return response.json()
    except Exception:
        pass
    return None


def update_user(nfc_id: str, is_adult: bool | None = None, balance: float | None = None) -> dict[str, Any] | None:
    """Update a user."""
    payload: dict[str, Any] = {}
    if is_adult is not None:
        payload["is_adult"] = is_adult
    if balance is not None:
        payload["balance"] = balance
    try:
        response = requests.put(f"{API_URL}/api/users/{nfc_id}", json=payload, timeout=2)
        if response.status_code == HTTP_OK:
            return response.json()
    except Exception:
        pass
    return None


def delete_user(nfc_id: str) -> bool:
    """Delete a user."""
    try:
        response = requests.delete(f"{API_URL}/api/users/{nfc_id}", timeout=2)
        return response.status_code == HTTP_NO_CONTENT
    except Exception:
        pass
    return False


def update_balance(nfc_id: str, amount: float) -> dict[str, Any] | None:
    """Update user balance."""
    try:
        response = requests.post(
            f"{API_URL}/api/balance/update",
            json={"nfc_id": nfc_id, "amount": amount},
            timeout=2,
        )
        if response.status_code == HTTP_OK:
            return response.json()
    except Exception:
        pass
    return None
