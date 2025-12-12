# tabs/topup_tab.py

import asyncio
import random

from store import UserStore
from theme import Styles

from nicegui import ui


class TopUpTab:
    """Top-Up tab: scan NFC, view balance, add/subtract funds."""

    def __init__(self, store: UserStore, tab) -> None:
        self.store = store
        self.card_id: str | None = None
        self.current_user: dict | None = None
        self.amount_value: float = 10.0
        self._scan_hint = (
            "Simulating NFC scan (sample users)..." if self.store.mock_nfc_enabled else "Hold a card to the reader..."
        )

        with ui.tab_panel(tab):
            ui.label("Top-Up user balance via NFC scan").classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.status_label = ui.label("Ready to scan").classes(Styles.TEXT_SECONDARY)
            with ui.row().classes("items-center mb-4"):
                self.scan_button = ui.button("Scan NFC card", icon="nfc", color="primary").classes("py-2")
                self.card_label = ui.label("No card scanned yet").classes(f"text-sm {Styles.TEXT_MUTED} text-center")

            # Balance display (hidden until scan)
            self.balance_container = ui.card().classes(
                f"{Styles.CARD} w-full mb-4 p-4 flex flex-col items-center text-center gap-2"
            )
            self.balance_container.visible = False
            with self.balance_container:
                ui.label("Current Balance").classes(f"text-lg {Styles.SUBHEADER}")
                self.balance_label = ui.label("€0.00").classes("text-4xl font-bold")

            # Top-up controls (hidden until scan)
            self.topup_container = ui.card().classes(f"{Styles.CARD} w-full mb-4 p-4 flex flex-col items-center gap-3")
            self.topup_container.visible = False
            with self.topup_container:
                with ui.grid(columns=2).classes("w-full max-w-md gap-3"):
                    for amount in [5, 10, 20, 50]:
                        ui.button(f"{amount}", icon="euro_symbol").classes("py-4 flex-1").on_click(
                            lambda a=amount: self.set_amount(float(a))
                        )
                self.amount_label = ui.label(self._format_amount()).classes("text-6xl my-4 font-bold text-center")
                with ui.grid(columns=4).classes("w-full max-w-md gap-2"):
                    for amount in [-5, -1, 1, 5]:
                        icon = "remove" if amount < 0 else "add"
                        ui.button(f"{abs(amount)}", icon=icon).classes("py-3").on_click(
                            lambda a=amount: self.change_amount(a)
                        )
                self.update_button = ui.button(
                    "Update Balance", icon="account_balance_wallet", color="secondary"
                ).classes("mt-6 py-3 w-full max-w-md")

        # Attach handlers
        self.scan_button.on_click(self.start_scan)
        self.update_button.on_click(self.update_balance)

    # --- UI handlers -------------------------------------------------

    def change_amount(self, number: float = 1.00) -> None:
        """Change the top-up amount by the given number."""
        self.amount_value += number
        self._refresh_amount_label()

    def set_amount(self, number: float) -> None:
        """Set the top-up amount to a fixed value."""
        self.amount_value = number
        self._refresh_amount_label()

    def _format_amount(self) -> str:
        """Format the amount for display."""
        return f"+ €{self.amount_value:.2f}"

    def _refresh_amount_label(self) -> None:
        """Update the visible amount label."""
        self.amount_label.text = self._format_amount()

    async def start_scan(self) -> None:
        """Start NFC scan using the configured (real or mocked) reader."""
        self.scan_button.disable()
        self.status_label.text = "Scanning NFC card..."
        self.card_label.text = self._scan_hint

        self.balance_container.visible = False
        self.topup_container.visible = False
        self.card_id = None
        self.current_user = None

        if self.store.mock_nfc_enabled:
            card_id = await self._mock_topup_scan()
        else:
            card_id = await self.store.nfc.one_shot(timeout=10.0, poll_interval=0.5)
        self.card_id = card_id

        if not card_id:
            self.status_label.text = "Scan timed out"
            self.card_label.text = "No card detected"
            ui.notify(
                "NFC scan timed out. Please try again.",
                color="warning",
                position="top-right",
            )
            self.scan_button.enable()
            return

        self.current_user = self.store.get_user(card_id)

        if self.current_user:
            self.status_label.text = "User found"
            self.card_label.text = f"Scanned card ID: {card_id}"
            self._update_balance_display()
            self.balance_container.visible = True
            self.topup_container.visible = True
            self.amount_value = 10.00
            self._refresh_amount_label()
        else:
            self.status_label.text = "User not found"
            self.card_label.text = f"Card ID {card_id} is not registered"
            ui.notify(
                "User not found. Please create user first.",
                color="warning",
                position="top-right",
            )

        self.scan_button.enable()

    def _update_balance_display(self):
        """Update the balance label with current user's balance."""
        if self.current_user:
            balance = self.current_user.get("balance", 10.0)
            self.balance_label.text = f"€{balance:.2f}"

    async def update_balance(self):
        """Update the user's balance."""
        if not self.card_id or not self.current_user:
            ui.notify("No user scanned!", color="negative", position="top-right")
            return

        amount = self.amount_value or 0
        if amount == 0:
            ui.notify("Please enter an amount to add.", color="warning", position="top-right")
            return

        self.update_button.disable()
        self.status_label.text = "Updating balance..."

        new_balance = self.store.update_balance(self.card_id, amount)

        # Refresh current user data
        self.current_user = self.store.get_user(self.card_id)
        self._update_balance_display()

        # Hide the top-up controls after successful update
        self.topup_container.visible = False
        self.balance_container.visible = False

        action = "added to" if amount > 0 else "removed from"
        self.status_label.text = f"€{abs(amount):.2f} {action} balance"
        ui.notify(
            f"Balance updated! New balance: €{new_balance:.2f}",
            color="positive",
            position="top-right",
        )

        self.update_button.enable()

    async def _mock_topup_scan(self) -> str | None:
        """Return a known user card id for top-up testing."""
        await asyncio.sleep(1.0)
        users = list(self.store.all_users().keys())
        if not users:
            return None
        return random.choice(users)


def build_topup_tab(tab, store: UserStore) -> TopUpTab:
    """Helper to construct the TopUpTab."""
    return TopUpTab(store, tab)
