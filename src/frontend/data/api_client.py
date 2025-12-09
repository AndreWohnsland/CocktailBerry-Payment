from typing import Any

import requests

API_URL = "http://localhost:8000"
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204


def fetch_nfc_id() -> str | None:
    """Poll NFC scanner for a card."""
    try:
        response = requests.get(f"{API_URL}/api/nfc/scan", timeout=2)
        if response.status_code == HTTP_OK:
            data = response.json()
            if data:
                return data.get("nfc_id")
    except Exception:
        pass
    return None


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


def create_user(nfc_id: str, name: str, is_adult: bool) -> dict[str, Any] | None:
    """Create a new user."""
    try:
        response = requests.post(
            f"{API_URL}/api/users",
            json={"nfc_id": nfc_id, "name": name, "is_adult": is_adult},
            timeout=2,
        )
        if response.status_code == HTTP_CREATED:
            return response.json()
    except Exception:
        pass
    return None


def update_user(nfc_id: str, name: str | None = None, is_adult: bool | None = None) -> dict[str, Any] | None:
    """Update a user."""
    payload = {}
    if name is not None:
        payload["name"] = name
    if is_adult is not None:
        payload["is_adult"] = is_adult
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
