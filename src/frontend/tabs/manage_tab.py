from collections.abc import Coroutine
from typing import Callable

from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.store import UserStore
from src.frontend.theme import Styles


class ManageTab:
    """Manage tab: shows list of users with delete buttons."""

    def __init__(self, store: UserStore, tab: Tab) -> None:
        self.store = store
        self.filter_value: str = ""

        with ui.tab_panel(tab):
            with ui.row().classes("items-center w-full mb-4"):
                self.filter_input = ui.input("Filter by Card ID", on_change=self.on_filter_change).classes("flex-grow")
                self.scan_button = (
                    ui.button("Scan Card", icon="nfc", color="primary").classes("py-2").on_click(self.scan_card)
                )
                self.clear_button = (
                    ui.button("Clear", icon="clear", color="neutral").classes("py-2").on_click(self.clear_filter)
                )

            self.users_column = ui.column().classes("w-full gap-2")

        # Register for changes and do initial render
        self.store.add_listener(self.refresh)
        self.refresh()

    def on_filter_change(self) -> None:
        """Update filter value and refresh the list."""
        self.filter_value = (self.filter_input.value or "").strip().upper()
        self.refresh()

    def clear_filter(self) -> None:
        """Clear the filter input."""
        self.filter_input.value = ""
        self.filter_value = ""
        self.refresh()

    async def scan_card(self) -> None:
        """Scan an NFC card and use it as the filter."""
        self.scan_button.disable()
        self.filter_input.value = "Scanning..."

        card_id = await self.store.nfc.one_shot(timeout=10.0, poll_interval=0.5)

        self.scan_button.enable()
        if not card_id:
            ui.notify(
                "NFC scan timed out. Please try again.",
                color="warning",
                position="top-right",
            )
            self.filter_input.value = self.filter_value
            return

        self.filter_input.value = card_id
        self.filter_value = card_id
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the user list from the store."""
        self.users_column.clear()
        users = self.store.all_users()

        # Apply filter if set
        if self.filter_value:
            users = {uid: data for uid, data in users.items() if self.filter_value in data["card_id"].upper()}

        if not users:
            with self.users_column:
                if self.filter_value:
                    ui.label(f"No users found matching '{self.filter_value}'.").classes(Styles.TEXT_MUTED)
                else:
                    ui.label("No users created yet.").classes(Styles.TEXT_MUTED)
            return

        with self.users_column:
            for user_id, data in sorted(users.items()):
                with ui.row().classes("items-center justify-between w-full"):
                    with ui.row().classes("items-center gap-2"):
                        ui.chip(
                            data["card_id"],
                            icon="credit_card",
                            color="primary",
                        )
                        is_adult = data.get("adult", False)
                        ui.chip(
                            "Adult" if is_adult else "Child",
                            icon="person" if is_adult else "child_care",
                            color="green" if is_adult else "gray",
                        )
                        balance = data.get("balance", 0.0)
                        ui.chip(
                            f"{balance:.2f}",
                            icon="euro",
                            color="secondary",
                        ).props("outline").classes("min-w-26 align-end")

                    def make_delete_handler(uid: str) -> Callable[[], Coroutine[None, None, None]]:
                        async def handler() -> None:
                            with ui.dialog() as dialog, ui.card():
                                ui.label(f"Are you sure you want to delete card {uid}?")
                                with ui.row():
                                    ui.button("Cancel", on_click=dialog.close)
                                    ui.button(
                                        "Delete",
                                        color="negative",
                                        on_click=lambda: dialog.submit(True),
                                    )
                            result = await dialog
                            if result:
                                # Notify before delete, since delete triggers refresh
                                # which clears the UI context
                                ui.notify(
                                    f"Card {uid} was deleted.",
                                    color="warning",
                                    position="top-right",
                                )
                                self.store.delete_user(uid)

                        return handler

                    ui.button("Delete", icon="delete", color="negative").on_click(make_delete_handler(user_id))


def build_manage_tab(tab: Tab, store: UserStore) -> ManageTab:
    return ManageTab(store, tab)
