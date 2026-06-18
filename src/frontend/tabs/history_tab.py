import asyncio
from collections.abc import Coroutine
from typing import Any

from nicegui import context, ui
from nicegui.elements.tabs import Tab

from src.frontend.components import NfcSearchBar
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
    <q-chip :icon="props.value < 0 ? 'remove' : 'add'" :color="props.value < 0 ? 'red' : 'green'" class="min-w-22 text-bold">
        {{ Math.abs(props.value).toFixed(2) }}
    </q-chip>
</q-td>
"""  # noqa: E501

BALANCE_SLOT = """
<q-td :props="props">
    <q-chip icon="euro" color="primary" class="min-w-22 text-bold">
        {{ props.value.toFixed(2) }}
    </q-chip>
</q-td>
"""

PAGE_SIZE = 10
# NFC UIDs are at least 8 hex chars (4-byte cards); don't fetch on shorter, partial input.
MIN_NFC_LEN = 8
SEARCH_DEBOUNCE_MS = 400


class HistoryTab:
    """History tab: search a card's transaction history by NFC ID (type or scan)."""

    def __init__(self, service: NFCService, tab: Tab) -> None:
        self.service = service
        self._background_tasks: set[asyncio.Task] = set()

        with ui.tab_panel(tab):
            # Captured here (a valid UI context) so background tasks can re-enter the
            # slot — asyncio tasks get an empty slot stack, which breaks ui.* calls.
            self._slot = context.slot
            ui.label(t.header_history).classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.search = NfcSearchBar(
                hint=t.mange_filter_hint,
                on_scan=self.service.nfc.one_shot,
                on_change=self._on_search,
                debounce_ms=SEARCH_DEBOUNCE_MS,
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

    def _add_task(self, coro: Coroutine) -> None:
        """Run a background task inside the UI slot, holding a reference so it isn't GC'd."""

        async def _runner() -> None:
            with self._slot:
                await coro

        task = asyncio.create_task(_runner())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def _on_search(self, value: str) -> None:
        """Schedule the async history fetch (on_change is synchronous)."""
        self._add_task(self._load_history(value))

    async def _load_history(self, value: str) -> None:
        """Fetch and show history for a full-length NFC ID; shorter input clears the table."""
        nfc_id = value.strip()
        if len(nfc_id) < MIN_NFC_LEN:
            self.table.rows = []
            return

        result = await self.service.get_nfc_history(nfc_id)

        # Discard a stale response if the input changed while the fetch was in flight.
        if nfc_id != self.search.value:
            return

        if is_success(result):
            self.table.rows = result.data
        elif is_err(result):
            self.table.rows = []
            ui.notify(str(result.error), type="negative", position="top-right")


def build_history_tab(tab: Tab, service: NFCService) -> HistoryTab:
    return HistoryTab(service, tab)
