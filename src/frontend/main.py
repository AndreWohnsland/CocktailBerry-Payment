from pathlib import Path

from nicegui import app, ui

from src.frontend.core.config import config as cfg
from src.frontend.i18n.translator import translations as t
from src.frontend.services import NFCService
from src.frontend.tabs.config_tab import build_config_tab
from src.frontend.tabs.create_tab import build_create_tab
from src.frontend.tabs.manage_tab import build_manage_tab
from src.frontend.tabs.topup_tab import build_topup_tab
from src.frontend.theme import Styles, apply_theme

static_file_path = Path(__file__).parent / "static"

APP_NAME = "CocktailBerry Payment Manager"


def _ui() -> None:
    # Apply theme before creating any UI elements
    apply_theme()

    service = NFCService()
    app.add_static_files("/static", static_file_path)
    ui.button.default_classes("rounded-lg")

    with ui.header().classes("p-4 bg-surface"), ui.row().classes("items-center justify-center w-full"):
        ui.image("/static/berry.svg").classes("w-10 h-10")
        ui.label(APP_NAME).classes(f"text-3xl {Styles.HEADER}")

    with ui.column().classes("w-full max-w-2xl mx-auto mt-4"):
        with ui.tabs().classes("w-full") as tabs:
            tab_topup = ui.tab(t.tab_top_up, icon="payments").classes("px-8")
            tab_create = ui.tab(t.tab_create, icon="person_add").classes("px-8")
            tab_manage = ui.tab(t.tab_manage, icon="manage_accounts").classes("px-8")
            if cfg.can_change_settings:
                tab_config = ui.tab(t.tab_config, icon="settings").classes("px-8")

        with ui.tab_panels(tabs, value=tab_topup).classes("w-full px-4 rounded-2xl"):
            build_topup_tab(tab_topup, service)
            build_create_tab(tab_create, service)
            build_manage_tab(tab_manage, service)
            if cfg.can_change_settings:
                build_config_tab(tab_config)


def start_nicegui() -> None:
    ui.run(
        _ui,
        title=APP_NAME,
        reload=cfg.dev_mode,
        native=cfg.native_mode,
        fullscreen=cfg.full_screen,
        window_size=(900, 1200) if cfg.native_mode and not cfg.full_screen else None,
        favicon=static_file_path / "favicon.ico",
        language=cfg.language,  # type: ignore[arg-type]
    )
