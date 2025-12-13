import asyncio
import random
from typing import Any, Callable, Protocol

import httpx

from src.frontend.core.config import config as cfg
from src.frontend.core.nfc import NFCScanner
from src.frontend.models.nfc import Nfc


async def mock_nfc_scan() -> str:
    """Simulate a 3-second NFC scan and return a random card ID."""
    await asyncio.sleep(3)
    return "".join(random.choices("0123456789ABCDEF", k=8))


async def mock_post_to_backend(user_data: dict[str, Any]) -> None:
    """Simulate a remote backend POST (0.5s delay)."""
    await asyncio.sleep(0.5)
    print(f"[mock_post_to_backend] {user_data}")


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

    async def get_all_nfc(self) -> list[Nfc]:
        """Fetch all NFC users from backend and return as a list of `Nfc` models."""
        resp = await self._client.get("/users")
        resp.raise_for_status()
        data = resp.json()
        return [Nfc.model_validate(item) for item in data]

    async def get_nfc(self, nfc_id: str) -> Nfc | None:
        """Fetch a single user by NFC ID from backend, or return None if 404."""
        # try cache first
        resp = await self._client.get(f"/users/{nfc_id}")
        if resp.status_code == 404:  # noqa: PLR2004
            return None
        resp.raise_for_status()
        return Nfc.model_validate(resp.json())

    # --- Mutation methods --------------------------------------------

    async def create_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> str:
        """Create user via backend and notify listeners. Returns new user id."""
        payload = {"nfc_id": nfc_id, "is_adult": is_adult, "balance": balance}
        resp = await self._client.post("/users", json=payload)
        resp.raise_for_status()
        user = Nfc.model_validate(resp.json())
        self._notify()
        return user.nfc_id

    async def delete_nfc(self, nfc_id: str) -> None:
        """Delete user via backend and notify listeners."""
        resp = await self._client.delete(f"/users/{nfc_id}")
        # backend returns 204 on success; treat 404 as no-op
        if resp.status_code == 404:  # noqa: PLR2004
            return
        resp.raise_for_status()
        self._notify()

    async def update_balance(self, nfc_id: str, amount: float) -> float:
        """Update balance via backend and return the new balance."""
        payload = {"amount": amount}
        resp = await self._client.post(f"/users/{nfc_id}/balance/top-up", json=payload)
        resp.raise_for_status()
        user = Nfc.model_validate(resp.json())
        self._notify()
        return user.balance

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
