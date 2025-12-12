# tabs/topup_tab.py

import asyncio
import random

from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.components import AmountSelector, NfcScannerSection
from src.frontend.store import UserStore
from src.frontend.theme import Styles


class TopUpTab:
    """Top-Up tab: scan NFC, view balance, add/subtract funds."""

    def __init__(self, store: UserStore, tab: Tab) -> None:
        self.store = store
        self.current_user: dict | None = None
        self._scan_hint = (
            "Simulating NFC scan (sample users)..." if self.store.mock_nfc_enabled else "Hold a card to the reader..."
        )

        with ui.tab_panel(tab):
            ui.label("Top-Up user balance via NFC scan").classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.nfc_scanner = NfcScannerSection(
                scan_hint=self._scan_hint,
                on_scan=self._perform_scan,
                on_clear=self._on_clear,
                on_scan_complete=self._on_scan_complete,
            )

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
                self.amount_selector = AmountSelector(initial_value=10.0)
                self.update_button = ui.button(
                    "Update Balance", icon="account_balance_wallet", color="secondary"
                ).classes("mt-8 py-3 w-full max-w-md")

        # Attach handlers
        self.update_button.on_click(self.update_balance)

    # --- UI handlers -------------------------------------------------

    async def _perform_scan(self) -> str | None:
        """Perform the actual NFC scan."""
        self.balance_container.visible = False
        self.topup_container.visible = False
        self.current_user = None

        if self.store.mock_nfc_enabled:
            return await self._mock_topup_scan()
        return await self.store.nfc.one_shot(timeout=10.0, poll_interval=0.5)

    def _on_scan_complete(self, card_id: str | None) -> None:
        """Handle scan completion."""
        if not card_id:
            ui.notify(
                "NFC scan timed out. Please try again.",
                color="warning",
                position="top-right",
            )
            return

        self.current_user = self.store.get_user(card_id)

        if self.current_user:
            self.nfc_scanner.set_status("User found")
            self._update_balance_display()
            self.balance_container.visible = True
            self.topup_container.visible = True
            self.amount_selector.reset(10.0)
        else:
            self.nfc_scanner.set_status("User not found")
            self.nfc_scanner.set_card_label(f"Card ID {card_id} is not registered")
            ui.notify(
                "User not found. Please create user first.",
                color="warning",
                position="top-right",
            )

    def _on_clear(self) -> None:
        """Handle clear button press."""
        self.balance_container.visible = False
        self.topup_container.visible = False
        self.current_user = None

    def _update_balance_display(self) -> None:
        """Update the balance label with current user's balance."""
        if self.current_user:
            balance = self.current_user.get("balance", 10.0)
            self.balance_label.text = f"€{balance:.2f}"

    async def update_balance(self) -> None:
        """Update the user's balance."""
        if not self.nfc_scanner.card_id or not self.current_user:
            ui.notify("No user scanned!", color="negative", position="top-right")
            return

        amount = self.amount_selector.value
        if amount == 0:
            ui.notify("Please enter an amount to add.", color="warning", position="top-right")
            return

        self.update_button.disable()
        self.nfc_scanner.set_status("Updating balance...")

        new_balance = self.store.update_balance(self.nfc_scanner.card_id, amount)

        # Refresh current user data
        self.current_user = self.store.get_user(self.nfc_scanner.card_id)
        self._update_balance_display()

        # Hide the top-up controls and reset scanner after successful update
        self.topup_container.visible = False
        self.balance_container.visible = False
        self.current_user = None

        action = "added to" if amount > 0 else "removed from"
        self.nfc_scanner.reset()
        self.nfc_scanner.set_status(f"€{abs(amount):.2f} {action} balance")
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


def build_topup_tab(tab: Tab, store: UserStore) -> TopUpTab:
    return TopUpTab(store, tab)
