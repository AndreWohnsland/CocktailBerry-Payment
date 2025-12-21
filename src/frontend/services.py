import asyncio
import contextlib
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Protocol, TypeGuard

import httpx

from src.frontend.core.config import config as cfg
from src.frontend.core.nfc import NFCScanner
from src.frontend.i18n.translator import translations as t
from src.frontend.models.nfc import Nfc


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


async def mock_nfc_scan() -> str:
    """Simulate a 3-second NFC scan and return a random card ID."""
    await asyncio.sleep(3)
    return "".join(random.choices("0123456789ABCDEF", k=8))


class NFCInterface(Protocol):
    """Minimal interface for NFC scanners used by the UI."""

    async def one_shot(self, timeout: float = cfg.nfc_timeout, poll_interval: float = 0.5) -> str | None:
        """Scan for a single NFC card."""


class NFCService:
    """Simple in-memory user store with change listeners."""

    def __init__(self) -> None:
        self.api_url = cfg.api_url
        self.api_key = cfg.api_key
        # httpx AsyncClient created once for reuse
        self._client = httpx.AsyncClient(base_url=self.api_url, headers={"x-api-key": self.api_key})
        self._listeners: list[Callable[[], None]] = []
        self.mock_nfc_enabled = cfg.mock_nfc
        self.nfc: NFCInterface = self._create_nfc_interface()

    # --- State access ------------------------------------------------

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
        if resp.status_code == 404:  # noqa: PLR2004
            return None
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    @run_catching
    async def get_nfc_history(self, nfc_id: str) -> list[dict[str, Any]]:
        """Fetch transaction history for a user by NFC ID."""
        resp = await self._client.get(f"/users/{nfc_id}/history")
        if resp.status_code == 404:  # noqa: PLR2004
            raise RuntimeError(t.nfc_card_not_registered.format(nfc_id=nfc_id))
        resp.raise_for_status()
        return resp.json()

    # --- Mutation methods --------------------------------------------

    @run_catching
    async def create_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> Nfc:
        """Create user via backend and notify listeners. Returns new user id."""
        payload = {"nfc_id": nfc_id, "is_adult": is_adult, "balance": balance}
        resp = await self._client.post("/users", json=payload)
        resp.raise_for_status()
        user = Nfc.model_validate(resp.json())
        self._notify()
        return user

    @run_catching
    async def delete_nfc(self, nfc_id: str) -> None:
        """Delete user via backend and notify listeners."""
        resp = await self._client.delete(f"/users/{nfc_id}")
        if resp.status_code == 404:  # noqa: PLR2004
            raise RuntimeError(t.nfc_card_not_registered.format(nfc_id=nfc_id))
        resp.raise_for_status()
        self._notify()

    @run_catching
    async def update_balance(self, nfc_id: str, amount: float) -> Nfc:
        """Update balance via backend and return an UpdateBalanceResult."""
        payload = {"amount": amount}
        resp = await self._client.post(f"/users/{nfc_id}/balance/top-up", json=payload)
        resp.raise_for_status()
        user = Nfc.model_validate(resp.json())
        self._notify()
        return user

    # --- Listener management ----------------------------------------

    def add_listener(self, listener: Callable[[], None]) -> None:
        """Register a callback that is called whenever users change."""
        self._listeners.append(listener)

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    # --- NFC selection ----------------------------------------------

    def _create_nfc_interface(self) -> NFCInterface:
        """Return the configured NFC interface (real or mocked)."""

        class MockNFC:
            """Lightweight wrapper to present the same interface as NFCScanner."""

            async def one_shot(self, timeout: float = 10.0, poll_interval: float = 0.5) -> str | None:
                return await mock_nfc_scan()

        if self.mock_nfc_enabled:
            return MockNFC()
        return NFCScanner()
