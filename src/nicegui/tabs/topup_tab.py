# tabs/topup_tab.py

from nicegui import ui
from store import UserStore
from services import mock_nfc_scan
from theme import Styles


class TopUpTab:
    """Top-Up tab: scan NFC, view balance, add/subtract funds."""

    def __init__(self, store: UserStore, tab) -> None:
        self.store = store
        self.card_id: str | None = None
        self.current_user: dict | None = None

        with ui.tab_panel(tab):
            ui.label("Top-Up user balance via NFC scan").classes(
                f"text-xl my-2 {Styles.SUBHEADER}"
            )

            self.status_label = ui.label("Ready to scan").classes(Styles.TEXT_SECONDARY)
            with ui.row().classes("items-center mb-4"):
                self.scan_button = ui.button(
                    "Scan NFC card", icon="nfc", color="primary"
                )
                self.card_label = ui.label("No card scanned yet").classes(
                    f"text-sm {Styles.TEXT_MUTED}"
                )

            # Balance display (hidden until scan)
            self.balance_container = ui.column().classes("mb-4")
            self.balance_container.visible = False
            with self.balance_container:
                ui.label("Current Balance").classes(f"text-lg {Styles.SUBHEADER}")
                self.balance_label = ui.label("€0.00").classes(
                    "text-2xl font-bold text-primary"
                )

            # Top-up controls (hidden until scan)
            self.topup_container = ui.column().classes("mb-4")
            self.topup_container.visible = False
            with self.topup_container:
                ui.label("Amount to add").classes(f"text-sm {Styles.TEXT_MUTED}")
                with ui.row().classes("items-center gap-2"):
                    self.minus_button = ui.button("-", color="secondary").classes(
                        "w-12"
                    )
                    self.amount_input = ui.number(
                        value=1.00, format="%.2f", step=0.01
                    ).classes("w-24")
                    self.plus_button = ui.button("+", color="secondary").classes("w-12")

                self.update_button = ui.button(
                    "Update Balance", icon="account_balance_wallet", color="primary"
                ).classes("mt-4")

        # Attach handlers
        self.scan_button.on_click(self.start_scan)
        self.minus_button.on_click(self.decrement_amount)
        self.plus_button.on_click(self.increment_amount)
        self.update_button.on_click(self.update_balance)

    # --- UI handlers -------------------------------------------------

    def increment_amount(self):
        """Increment the top-up amount by 1.00."""
        self.amount_input.value = (self.amount_input.value or 0) + 1.00

    def decrement_amount(self):
        """Decrement the top-up amount by 1.00."""
        self.amount_input.value = (self.amount_input.value or 0) - 1.00

    async def start_scan(self):
        """Start NFC scan (mocked)."""
        self.scan_button.disable()
        self.status_label.text = "Scanning NFC card..."
        self.card_label.text = "Hold a card to the reader (mock, 5 seconds)..."

        self.balance_container.visible = False
        self.topup_container.visible = False
        self.card_id = None
        self.current_user = None

        card_id = await mock_nfc_scan()

        self.card_id = card_id
        self.current_user = self.store.get_user(card_id)

        if self.current_user:
            self.status_label.text = "User found"
            self.card_label.text = f"Scanned card ID: {card_id}"
            self._update_balance_display()
            self.balance_container.visible = True
            self.topup_container.visible = True
            self.amount_input.value = 1.00
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

        amount = self.amount_input.value or 0
        if amount == 0:
            ui.notify(
                "Please enter an amount to add.", color="warning", position="top-right"
            )
            return

        self.update_button.disable()
        self.status_label.text = "Updating balance..."

        new_balance = self.store.update_balance(self.card_id, amount)

        # Refresh current user data
        self.current_user = self.store.get_user(self.card_id)
        self._update_balance_display()

        action = "added to" if amount > 0 else "removed from"
        self.status_label.text = f"€{abs(amount):.2f} {action} balance"
        ui.notify(
            f"Balance updated! New balance: €{new_balance:.2f}",
            color="positive",
            position="top-right",
        )

        self.update_button.enable()


def build_topup_tab(tab, store: UserStore) -> TopUpTab:
    """Helper to construct the TopUpTab."""
    return TopUpTab(store, tab)
