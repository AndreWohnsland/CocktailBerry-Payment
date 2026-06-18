import asyncio
import random
from collections.abc import Callable
from typing import Any, Protocol

import httpx

from src.frontend.core.config import config as cfg
from src.frontend.core.nfc import NFCScanner
from src.frontend.core.payment_api import PaymentApi, Result, is_err, is_success
from src.frontend.models.nfc import Nfc

# Re-exported so tabs keep importing the Result guards from here unchanged.
__all__ = ["NFCInterface", "NFCService", "is_err", "is_success"]


async def mock_nfc_scan() -> str:
    """Simulate a 3-second NFC scan and return a random card ID."""
    await asyncio.sleep(3)
    return "".join(random.choices("0123456789ABCDEF", k=8))


class NFCInterface(Protocol):
    """Minimal interface for NFC scanners used by the UI."""

    async def one_shot(self, timeout: float = cfg.nfc_timeout, poll_interval: float = 0.5) -> str | None:
        """Scan for a single NFC card."""


class NFCService:
    """Facade for the GUI: the backend client, the NFC scanner, and UI change listeners.

    Read calls delegate straight to `PaymentApi`; mutations delegate and then notify
    listeners on success so other tabs refresh.
    """

    def __init__(self) -> None:
        client = httpx.AsyncClient(base_url=cfg.api_url, headers={"x-api-key": cfg.api_key})
        self.api = PaymentApi(client)
        self._listeners: list[Callable[[], None]] = []
        self.mock_nfc_enabled = cfg.mock_nfc
        self.nfc: NFCInterface = self._create_nfc_interface()

    # --- State access (straight delegation) --------------------------

    async def get_all_nfc(self) -> Result[list[Nfc]]:
        return await self.api.get_all_nfc()

    async def get_nfc(self, nfc_id: str) -> Result[Nfc | None]:
        return await self.api.get_nfc(nfc_id)

    async def get_nfc_history(self, nfc_id: str) -> Result[list[dict[str, Any]]]:
        return await self.api.get_nfc_history(nfc_id)

    # --- Mutations (delegate, then notify on success) ----------------

    async def create_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> Result[Nfc]:
        result = await self.api.create_nfc(nfc_id, is_adult, balance)
        if is_success(result):
            self._notify()
        return result

    async def update_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> Result[Nfc]:
        result = await self.api.update_nfc(nfc_id, is_adult, balance)
        if is_success(result):
            self._notify()
        return result

    async def delete_nfc(self, nfc_id: str) -> Result[None]:
        result = await self.api.delete_nfc(nfc_id)
        if is_success(result):
            self._notify()
        return result

    async def update_balance(self, nfc_id: str, amount: float) -> Result[Nfc]:
        result = await self.api.update_balance(nfc_id, amount)
        if is_success(result):
            self._notify()
        return result

    async def aclose(self) -> None:
        """Close the underlying HTTP client. Should be called on app shutdown."""
        await self.api.aclose()

    # --- Listener management -----------------------------------------

    def add_listener(self, listener: Callable[[], None]) -> None:
        """Register a callback that is called whenever users change."""
        self._listeners.append(listener)

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    # --- NFC selection -----------------------------------------------

    def _create_nfc_interface(self) -> NFCInterface:
        """Return the configured NFC interface (real or mocked)."""

        class MockNFC:
            """Lightweight wrapper to present the same interface as NFCScanner."""

            async def one_shot(self, timeout: float = 10.0, poll_interval: float = 0.5) -> str | None:
                return await mock_nfc_scan()

        if self.mock_nfc_enabled:
            return MockNFC()
        return NFCScanner()
