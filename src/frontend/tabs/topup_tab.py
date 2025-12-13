# tabs/topup_tab.py

import asyncio
import random

from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.components import AmountSelector, NfcScannerSection
from src.frontend.core.config import config as cfg
from src.frontend.i18n.translator import translations as t
from src.frontend.models.nfc import Nfc
from src.frontend.services import NFCService
from src.frontend.theme import Styles


class TopUpTab:
    """Top-Up tab: scan NFC, view balance, add/subtract funds."""

    def __init__(self, service: NFCService, tab: Tab) -> None:
        self.service = service
        self.current_user: Nfc | None = None
        self._scan_hint = t.nfc_simulate_hint if self.service.mock_nfc_enabled else t.nfc_scan_hint

        with ui.tab_panel(tab):
            ui.label(t.header_top_up).classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.nfc_scanner = NfcScannerSection(
                scan_hint=self._scan_hint,
                on_scan=self._perform_scan,
                on_clear=self._on_clear,
                on_scan_complete=self._on_scan_complete,
            )

            # Balance display (hidden until scan)
            self.balance_container = ui.card().classes(
                f"{Styles.CARD} w-full mb-6 p-4 flex flex-col items-center text-center gap-2"
            )
            self.balance_container.visible = False
            with self.balance_container:
                ui.label(t.balance).classes(f"text-lg {Styles.SUBHEADER}")
                self.balance_label = ui.label("€0.00").classes("text-4xl font-bold")

            # Top-up controls (hidden until scan)
            self.topup_container = ui.card().classes(
                f"{Styles.CARD} w-full mb-4 p-4 py-6 flex flex-col items-center gap-3"
            )
            self.topup_container.visible = False
            with self.topup_container:
                self.amount_selector = AmountSelector(initial_value=cfg.default_balance)
                self.update_button = ui.button(
                    t.balance_update, icon="account_balance_wallet", color="secondary"
                ).classes("mt-8 py-3 w-full max-w-md text-xl font-bold")

        # Attach handlers
        self.update_button.on_click(self.update_balance)

    # --- UI handlers -------------------------------------------------

    async def _perform_scan(self) -> str | None:
        """Perform the actual NFC scan."""
        self.balance_container.visible = False
        self.topup_container.visible = False
        self.current_user = None

        if self.service.mock_nfc_enabled:
            return await self._mock_topup_scan()
        return await self.service.nfc.one_shot()

    async def _on_scan_complete(self, nfc_id: str | None) -> None:
        """Handle scan completion (async)."""
        if not nfc_id:
            ui.notify(t.nfc_timeout, type="warning", position="top-right")
            return

        self.current_user = await self.service.get_nfc(nfc_id)

        if self.current_user:
            self.nfc_scanner.set_status(t.nfc_found)
            self._update_balance_display()
            self.balance_container.visible = True
            self.topup_container.visible = True
            self.amount_selector.reset(cfg.default_balance)
        else:
            self.nfc_scanner.set_status(t.nfc_not_found)
            self.nfc_scanner.set_card_label(t.nfc_card_not_registered.format(nfc_id=nfc_id))
            ui.notify(
                t.nfc_not_found_detail,
                type="warning",
                position="top-right",
            )

    def _on_clear(self) -> None:
        """Handle clear button press."""
        self.balance_container.visible = False
        self.topup_container.visible = False
        self.current_user = None

    def _update_balance_display(self) -> None:
        """Update the balance label with current user's balance."""
        if user := self.current_user:
            self.balance_label.text = f"€{user.balance:.2f}"

    async def update_balance(self) -> None:
        """Update the user's balance."""
        if not self.nfc_scanner.nfc_id or not self.current_user:
            # should not happen due to UI state, but just in case
            ui.notify("No user scanned!", type="negative", position="top-right")
            return

        amount = self.amount_selector.value
        if amount == 0:
            ui.notify(t.balance_no_amount_given, type="warning", position="top-right")
            return

        self.update_button.disable()
        self.nfc_scanner.set_status(t.balance_updating)

        new_balance = await self.service.update_balance(self.nfc_scanner.nfc_id, amount)

        # Refresh current user data
        self.current_user = await self.service.get_nfc(self.nfc_scanner.nfc_id)
        self._update_balance_display()

        # Hide the top-up controls and reset scanner after successful update
        self.topup_container.visible = False
        self.balance_container.visible = False
        self.current_user = None

        self.nfc_scanner.reset()
        self.nfc_scanner.set_status(t.balance_notify_add.format(amount=amount))
        ui.notify(
            t.balance_updated.format(balance=new_balance),
            type="positive",
            position="top-right",
        )

        self.update_button.enable()

    async def _mock_topup_scan(self) -> str | None:
        """Return a known user card id for top-up testing."""
        await asyncio.sleep(1.0)
        users = await self.service.get_all_nfc()
        if not users:
            return None
        return random.choice([u.nfc_id for u in users])


def build_topup_tab(tab: Tab, service: NFCService) -> TopUpTab:
    return TopUpTab(service, tab)
