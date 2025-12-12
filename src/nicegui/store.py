# store.py

from typing import Any, Callable

from core.nfc import NFCScanner


class UserStore:
    """Simple in-memory user store with change listeners."""

    DEFAULT_BALANCE = 10.0

    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {
            "12345678": {"card_id": "12345678", "adult": True, "balance": 12.0},
            "12345679": {"card_id": "12345679", "adult": True, "balance": 10.0},
            "12345680": {"card_id": "12345680", "adult": False, "balance": 20.0},
            "12345681": {"card_id": "12345681", "adult": True, "balance": 0.0},
            "12345682": {"card_id": "12345682", "adult": False, "balance": 123.0},
            "12345683": {"card_id": "12345683", "adult": True, "balance": 10.0},
            "12345684": {"card_id": "12345684", "adult": False, "balance": 1340.0},
        }
        self._listeners: list[Callable[[], None]] = []
        self.nfc = NFCScanner()

    # --- State access ------------------------------------------------

    def all_users(self) -> dict[str, dict[str, Any]]:
        """Return a copy of all users."""
        return dict(self._users)

    def get_user(self, card_id: str) -> dict[str, Any] | None:
        """Return a user by card_id, or None if not found."""
        return self._users.get(card_id)

    # --- Mutation methods --------------------------------------------

    def add_user(self, data: dict[str, Any]) -> int:
        """Add a user and notify listeners. Returns new user id."""
        uid = data["card_id"]
        # Ensure balance is set with default if not provided
        if "balance" not in data:
            data["balance"] = self.DEFAULT_BALANCE
        self._users[uid] = data
        self._notify()
        return uid

    def delete_user(self, user_id: str) -> None:
        """Delete a user if it exists and notify listeners."""
        if user_id in self._users:
            del self._users[user_id]
            self._notify()

    def update_balance(self, card_id: str, amount: float) -> float:
        """Update a user's balance by adding the given amount. Returns new balance."""
        if card_id in self._users:
            current = self._users[card_id].get("balance", self.DEFAULT_BALANCE)
            new_balance = current + amount
            self._users[card_id]["balance"] = new_balance
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
