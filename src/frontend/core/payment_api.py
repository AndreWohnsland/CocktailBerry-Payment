"""Typed client for the payment backend — the seam the GUI talks through.

Every method returns a ``Result`` (``Success`` | ``Err``); ``run_catching`` turns
any exception (incl. an httpx error body's ``{"detail": ...}``) into a localized
``Err``. The httpx client is injected, so tests drive this through an
``httpx.MockTransport`` with no server — the interface is the test surface.
"""

import contextlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeGuard

import httpx

from src.frontend.i18n.translator import translations as t
from src.frontend.models.nfc import Nfc

_HTTP_NOT_FOUND = 404


@dataclass
class Success[T]:
    data: T


@dataclass
class Err:
    error: str


type Result[T] = Success[T] | Err


def run_catching[**P, T](
    fn: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[Result[T]]]:
    @wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T]:
        try:
            return Success(await fn(*args, **kwargs))
        except Exception as exc:
            reason: str = str(exc)
            # If this is an HTTP error from httpx, try to surface the
            # server-provided error body (commonly {'detail': '...'}).
            if isinstance(exc, httpx.HTTPStatusError):
                try:
                    body = exc.response.json()
                    reason = body["detail"] if isinstance(body, dict) and "detail" in body else str(body)
                except Exception:
                    with contextlib.suppress(Exception):
                        reason = exc.response.text or reason
            return Err(error=t.request_error.format(reason=str(reason)))

    return wrapper


def is_success[T](result: Result[T]) -> TypeGuard[Success[T]]:
    return isinstance(result, Success)


def is_err(result: Result[Any]) -> TypeGuard[Err]:
    return isinstance(result, Err)


class PaymentApi:
    """Backend client. Pure: no UI listeners, no scanner, no config reads."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    @run_catching
    async def get_all_nfc(self) -> list[Nfc]:
        """Fetch all NFC users from backend and return as a list of `Nfc` models."""
        resp = await self._client.get("/users")
        resp.raise_for_status()
        return [Nfc.model_validate(item) for item in resp.json()]

    @run_catching
    async def get_nfc(self, nfc_id: str) -> Nfc | None:
        """Fetch a single user by NFC ID from backend, or return None if 404."""
        resp = await self._client.get(f"/users/{nfc_id}")
        if resp.status_code == _HTTP_NOT_FOUND:
            return None
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    @run_catching
    async def get_nfc_history(self, nfc_id: str) -> list[dict[str, Any]]:
        """Fetch transaction history for a user by NFC ID."""
        resp = await self._client.get(f"/users/{nfc_id}/history")
        if resp.status_code == _HTTP_NOT_FOUND:
            raise RuntimeError(t.nfc_card_not_registered.format(nfc_id=nfc_id))
        resp.raise_for_status()
        return resp.json()

    @run_catching
    async def create_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> Nfc:
        """Create a user via backend."""
        payload = {"nfc_id": nfc_id, "is_adult": is_adult, "balance": balance}
        resp = await self._client.post("/users", json=payload)
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    @run_catching
    async def update_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> Nfc:
        """Update a user via backend."""
        payload = {"is_adult": is_adult, "balance": balance}
        resp = await self._client.put(f"/users/{nfc_id}", json=payload)
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    @run_catching
    async def delete_nfc(self, nfc_id: str) -> None:
        """Delete a user via backend."""
        resp = await self._client.delete(f"/users/{nfc_id}")
        if resp.status_code == _HTTP_NOT_FOUND:
            raise RuntimeError(t.nfc_card_not_registered.format(nfc_id=nfc_id))
        resp.raise_for_status()

    @run_catching
    async def update_balance(self, nfc_id: str, amount: float) -> Nfc:
        """Top up (or subtract from) a user's balance via backend."""
        payload = {"amount": amount}
        resp = await self._client.post(f"/users/{nfc_id}/balance/top-up", json=payload)
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    async def aclose(self) -> None:
        """Close the underlying HTTP client. Should be called on app shutdown."""
        await self._client.aclose()
