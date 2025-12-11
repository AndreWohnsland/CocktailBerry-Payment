# main.py

from nicegui import ui, app
from store import UserStore
from tabs.create_tab import build_create_tab
from tabs.manage_tab import build_manage_tab
from tabs.topup_tab import build_topup_tab
from theme import apply_theme, Styles


def main():
    # Apply theme before creating any UI elements
    apply_theme()

    store = UserStore()
    app.add_static_files("/static", "static")

    with ui.column().classes("w-full max-w-2xl mx-auto mt-10"):
        with ui.row().classes("items-center justify-center w-full mb-2"):
            ui.icon("local_bar", size="2.5rem").classes("text-secondary")
            ui.label("CocktailBerry Payment Management").classes(
                f"text-3xl {Styles.HEADER}"
            )

        with ui.tabs().classes("w-full") as tabs:
            tab_topup = ui.tab("Top-Up", icon="payments").classes("px-12")
            tab_create = ui.tab("Create", icon="person_add").classes("px-12")
            tab_manage = ui.tab("Manage", icon="manage_accounts").classes("px-12")

        with ui.tab_panels(tabs, value=tab_topup).classes("w-full px-4 rounded-2xl"):
            build_topup_tab(tab_topup, store)
            build_create_tab(tab_create, store)
            build_manage_tab(tab_manage, store)

    ui.run(title="CocktailBerry Payment", favicon="🍹")


main()
