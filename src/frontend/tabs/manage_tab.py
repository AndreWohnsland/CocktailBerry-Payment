from typing import Any

from nicegui import events, ui
from nicegui.elements.tabs import Tab

from src.frontend.i18n.translator import translations as t
from src.frontend.store import UserStore

# Table column definitions
TABLE_COLUMNS: list[dict[str, Any]] = [
    {"name": "card_id", "label": "NFC ID", "field": "card_id", "align": "left", "sortable": True},
    {"name": "status", "label": "Status", "field": "adult", "align": "left", "sortable": True},
    {"name": "balance", "label": t.balance, "field": "balance", "align": "left", "sortable": True},
    {"name": "action", "label": "Action", "field": "action", "align": "left"},
]

# Slot templates for custom cell rendering
CARD_ID_SLOT = """
<q-td :props="props">
    <q-chip icon="credit_card" color="primary" text-color="white">
        {{ props.row.card_id }}
    </q-chip>
</q-td>
"""

STATUS_SLOT = f"""
<q-td :props="props">
    <q-chip
        :icon="props.row.adult ? 'person' : 'child_care'"
        :color="props.row.adult ? 'green' : 'grey'"
        text-color="white"
    >
        {{{{ props.row.adult ? '{t.adult}' : '{t.child}' }}}}
    </q-chip>
</q-td>
"""

BALANCE_SLOT = """
<q-td :props="props">
    <q-chip icon="euro" color="secondary" outline class="min-w-26">
        {{ props.row.balance.toFixed(2) }}
    </q-chip>
</q-td>
"""

ACTION_SLOT = f"""
<q-td :props="props">
    <q-btn
        icon="delete"
        color="negative"
        label="{t.delete}"
        flat
        dense
        @click="() => $parent.$emit('delete', props.row)"
    />
</q-td>
"""

PAGE_SIZE = 10


class ManageTab:
    """Manage tab: shows list of users with delete buttons using a paginated table."""

    def __init__(self, store: UserStore, tab: Tab) -> None:
        self.store = store
        self.filter_value: str = ""

        with ui.tab_panel(tab):
            with ui.row().classes("items-center w-full mb-4"):
                self.filter_input = ui.input(t.mange_filter_hint, on_change=self._on_filter_change).classes("flex-grow")
                self.scan_button = (
                    ui.button(t.nfc_scan, icon="nfc", color="primary").classes("py-2").on_click(self._scan_card)
                )
                self.clear_button = (
                    ui.button(t.clear, icon="clear", color="neutral").classes("py-2").on_click(self._clear_filter)
                )

            self.table = (
                ui.table(
                    columns=TABLE_COLUMNS,
                    rows=[],
                    row_key="id",
                    pagination=PAGE_SIZE,
                )
                .classes("w-full mb-4")
                .props("flat bordered")
            )

            self.table.add_slot("body-cell-card_id", CARD_ID_SLOT)
            self.table.add_slot("body-cell-status", STATUS_SLOT)
            self.table.add_slot("body-cell-balance", BALANCE_SLOT)
            self.table.add_slot("body-cell-action", ACTION_SLOT)

            self.table.on("delete", self._on_delete)

        # Bind filter input to table's built-in filter
        self.filter_input.bind_value_to(self.table, "filter")

        # Register for changes and do initial render
        self.store.add_listener(self._refresh)
        self._refresh()

    def _on_filter_change(self) -> None:
        """Update filter value state."""
        self.filter_value = (self.filter_input.value or "").strip()

    def _clear_filter(self) -> None:
        """Clear the filter input."""
        self.filter_input.value = ""
        self.filter_value = ""

    async def _scan_card(self) -> None:
        """Scan an NFC card and use it as the filter."""
        self.scan_button.disable()
        original_value = self.filter_input.value
        self.filter_input.value = "Scanning..."

        card_id = await self.store.nfc.one_shot(timeout=10.0, poll_interval=0.5)

        self.scan_button.enable()
        if not card_id:
            ui.notify(
                t.nfc_timeout,
                type="warning",
                position="top-right",
            )
            self.filter_input.value = original_value or ""
            return

        self.filter_input.value = card_id
        self.filter_value = card_id

    async def _on_delete(self, e: events.GenericEventArguments) -> None:
        """Handle delete button click from table row."""
        row = e.args
        user_id = row["id"]
        card_id = row["card_id"]

        with ui.dialog() as dialog, ui.card():
            ui.label(t.manage_delete_confirm.format(card_id=card_id))
            with ui.row().classes("w-full flex justify-between items-center mt-2"):
                ui.button(
                    t.delete,
                    color="negative",
                    on_click=lambda: dialog.submit(True),
                )
                ui.button(t.cancel, on_click=dialog.close)

        result = await dialog
        if result:
            ui.notify(
                t.manage_card_deleted.format(card_id=card_id),
                type="warning",
                position="top-right",
            )
            self.store.delete_user(user_id)

    def _refresh(self) -> None:
        """Update table rows from the store."""
        users = self.store.all_users()

        rows = [
            {
                "id": user_id,
                "card_id": data["card_id"],
                "adult": data.get("adult", False),
                "balance": data.get("balance", 0.0),
            }
            for user_id, data in sorted(users.items())
        ]

        self.table.update_rows(rows)


def build_manage_tab(tab: Tab, store: UserStore) -> ManageTab:
    return ManageTab(store, tab)
