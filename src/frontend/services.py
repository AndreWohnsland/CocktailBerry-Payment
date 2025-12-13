import asyncio
import random
from typing import Any, Callable, Protocol

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
        self._nfc_data: dict[str, Nfc] = {
            f"{10000000 + i}": Nfc(nfc_id=f"{10000000 + i}", is_adult=i % 2 == 0, balance=float(i * 3))
            for i in range(100)
        }
        self._listeners: list[Callable[[], None]] = []
        self.mock_nfc_enabled = cfg.mock_nfc
        self.nfc: NFCInterface = self._create_nfc_interface()

    # --- State access ------------------------------------------------

    def get_all_nfc(self) -> dict[str, Nfc]:
        """Return a copy of all users."""
        return dict(self._nfc_data)

    def get_nfc(self, nfc_id: str) -> Nfc | None:
        """Return a user by nfc_id, or None if not found."""
        return self._nfc_data.get(nfc_id)

    # --- Mutation methods --------------------------------------------

    def create_nfc(self, nfc_id: str, is_adult: bool, balance: float) -> str:
        """Add a user and notify listeners. Returns new user id."""
        self._nfc_data[nfc_id] = Nfc(
            nfc_id=nfc_id,
            is_adult=is_adult,
            balance=balance,
        )
        self._notify()
        return nfc_id

    def delete_nfc(self, nfc_id: str) -> None:
        """Delete a user if it exists and notify listeners."""
        if nfc_id in self._nfc_data:
            del self._nfc_data[nfc_id]
            self._notify()

    def update_balance(self, nfc_id: str, amount: float) -> float:
        """Update a user's balance by adding the given amount. Returns new balance."""
        if nfc_id in self._nfc_data:
            current = self._nfc_data[nfc_id].balance
            new_balance = current + amount
            self._nfc_data[nfc_id].balance = new_balance
            self._notify()
            return new_balance
        return 0.0

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
