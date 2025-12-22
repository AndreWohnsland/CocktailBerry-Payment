from typing import Any

from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.components.nfc_scanner import NfcScannerSection
from src.frontend.i18n.translator import translations as t
from src.frontend.services import NFCService, is_err, is_success
from src.frontend.theme import Styles

TABLE_COLUMNS: list[dict[str, Any]] = [
    {
        "name": "created_at",
        "label": t.created_at,
        "field": "created_at",
        "align": "left",
        "sortable": True,
    },
    {"name": "description", "label": t.action, "field": "description", "align": "left"},
    {"name": "amount", "label": t.amount, "field": "amount", "align": "left"},
    {"name": "current_balance", "label": t.balance, "field": "current_balance", "align": "left"},
]

AMOUNT_SLOT = """
<q-td :props="props">
    <q-chip :color="props.value < 0 ? 'red' : 'green'" class="text-bold">
        {{ props.value }}
    </q-chip>
</q-td>
"""

BALANCE_SLOT = """
<q-td :props="props">
    <q-chip icon="euro" color="primary" class="min-w-22 text-bold">
        {{ props.row.current_balance.toFixed(2) }}
    </q-chip>
</q-td>
"""

PAGE_SIZE = 10


class HistoryTab:
    """History tab: shows list of users with delete buttons using a paginated table."""

    def __init__(self, service: NFCService, tab: Tab) -> None:
        self.service = service
        self.tab = tab
        self._scan_hint = t.nfc_simulate_hint if self.service.mock_nfc_enabled else t.nfc_scan_hint

        with ui.tab_panel(tab):
            ui.label(t.header_history).classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.nfc_scanner = NfcScannerSection(
                scan_hint=self._scan_hint,
                on_scan=self._perform_scan,
                on_clear=self._clear_scan,
                on_scan_complete=self._on_scan_complete,
            )

            self.table = (
                ui.table(
                    columns=TABLE_COLUMNS,
                    rows=[],
                    row_key="nfc_id",
                    pagination=PAGE_SIZE,
                )
                .classes("w-full mb-4")
                .props("flat bordered")
            )

            self.table.add_slot("body-cell-amount", AMOUNT_SLOT)
            self.table.add_slot("body-cell-current_balance", BALANCE_SLOT)

    async def _perform_scan(self) -> str | None:
        """Perform the actual NFC scan."""
        return await self.service.nfc.one_shot()

    async def _on_scan_complete(self, nfc_id: str | None) -> None:
        """Handle scan completion."""
        if not nfc_id:
            ui.notify(t.nfc_timeout, type="warning", position="top-right")
            return

        result = await self.service.get_nfc_history(nfc_id)

        if is_err(result):
            ui.notify(str(result.error), type="negative", position="top-right")
            self.table.rows = []
            return

        if is_success(result):
            self.table.rows = result.data

    def _clear_scan(self) -> None:
        """Handle scan clearing."""
        self.table.rows = []


def build_history_tab(tab: Tab, service: NFCService) -> HistoryTab:
    return HistoryTab(service, tab)
