import platform
from dataclasses import dataclass
from typing import Any

from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.core.config import Config
from src.frontend.core.config import config as cfg
from src.frontend.i18n.translator import translations as t
from src.frontend.theme import Styles
from src.shared.helpers import read_env_file, set_user_env_vars, write_env_file

TOKEN_MASK = "************"


@dataclass
class ConfigFieldSpec:
    name: str
    label: str
    value_type: type
    masked: bool = False


CONFIG_FIELDS: list[ConfigFieldSpec] = [
    ConfigFieldSpec("api_key", t.config_label_api_key, str, masked=True),
    ConfigFieldSpec("api_address", t.config_label_api_address, str),
    ConfigFieldSpec("api_port", t.config_label_api_port, int),
    ConfigFieldSpec("native_mode", t.config_label_native_mode, bool),
    ConfigFieldSpec("full_screen", t.config_label_full_screen, bool),
    ConfigFieldSpec("language", t.config_label_language, str),
    ConfigFieldSpec("default_balance", t.config_label_default_balance, float),
    ConfigFieldSpec("nfc_timeout", t.config_label_nfc_timeout, float),
]


class ConfigFieldRow:
    """Single editable config row with display + edit toggle."""

    def __init__(self, config: Config, spec: ConfigFieldSpec) -> None:
        self.cfg = config
        self.spec = spec
        self.editing = False

        with (
            ui.element("div")
            .classes("grid items-center w-full gap-2 py-1")
            .style("grid-template-columns: 10rem 1fr auto;")
        ):
            ui.label(spec.label).classes("text-app-secondary font-medium truncate")
            with ui.element("div").classes("w-full h-8 flex items-center"):
                self.display_value = ui.label(self._format_value()).classes("w-full text-lg text-app-primary")
                self.editor = self._create_editor()
                self.editor.visible = False
            self.toggle_button = (
                ui.button(icon="edit")
                .props("flat round dense color=primary")
                .classes("justify-self-end")
                .on_click(self._toggle_edit)
            )

    def _create_editor(self) -> Any:
        """Create an editor matching the field type."""
        value = getattr(self.cfg, self.spec.name)
        if self.spec.value_type is bool:
            return ui.switch(value=bool(value)).props("dense").classes("w-full")
        if self.spec.value_type in (int, float):
            step = 1 if self.spec.value_type is int else 0.1
            return ui.number(value=value, step=step).props("dense hide-bottom-space borderless").classes("w-full")
        return ui.input(value=str(value)).props("dense hide-bottom-space borderless").classes("w-full")

    def _toggle_edit(self) -> None:
        """Switch between view and edit modes."""
        if self.editing:
            self._save_value()
        else:
            self._start_edit()

    def _start_edit(self) -> None:
        """Enable editing for the row."""
        self.editing = True
        self._sync_editor_value()
        self.display_value.visible = False
        self.editor.visible = True
        self._set_button_state(icon="save", color="secondary")

    def _save_value(self) -> None:
        """Persist changes to the config object."""
        try:
            new_value = self._coerce_value(self._get_editor_value())
        except ValueError:
            ui.notify(
                t.config_invalid_value.format(field=self.spec.label),
                type="negative",
                position="top-right",
            )
            return

        setattr(self.cfg, self.spec.name, new_value)
        self.display_value.text = self._format_value()
        self._persist_env_value(new_value)

        self.editing = False
        self.display_value.visible = True
        self.editor.visible = False
        self._set_button_state(icon="edit", color="primary")

        ui.notify(t.config_saved.format(field=self.spec.label), type="positive", position="top-right")

    def _get_editor_value(self) -> Any:
        """Return the current editor value."""
        return self.editor.value  # type: ignore[no-any-return]

    def _sync_editor_value(self) -> None:
        """Synchronize editor value with the current config value."""
        value = getattr(self.cfg, self.spec.name)
        if self.spec.value_type is bool:
            self.editor.value = bool(value)
        elif self.spec.value_type in (int, float):
            self.editor.value = value
        else:
            self.editor.value = str(value)

    def _coerce_value(self, raw: Any) -> Any:
        """Convert raw editor value to the desired type."""
        target = self.spec.value_type
        if target is bool:
            if isinstance(raw, bool):
                return raw
            text = str(raw).strip().lower()
            if text in {"true", "1", "yes", "on"}:
                return True
            if text in {"false", "0", "no", "off"}:
                return False
            raise ValueError

        if raw is None or raw == "":
            raise ValueError
        if target is int:
            return int(float(raw))
        if target is float:
            return float(raw)
        return str(raw)

    def _format_value(self) -> str:
        """Format value for display mode."""
        value = getattr(self.cfg, self.spec.name)
        if self.spec.masked:
            return TOKEN_MASK
        if isinstance(value, bool):
            return t.config_value_true if value else t.config_value_false
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    def _set_button_state(self, icon: str, color: str) -> None:
        """Update toggle button appearance."""
        self.toggle_button.props(f"icon={icon} color={color}")
        self.toggle_button.update()

    def _persist_env_value(self, new_value: Any) -> None:
        """Write updated setting to .env and OS environment."""
        env_key = self.spec.name.upper()
        env_values = read_env_file()
        env_values[env_key] = self._serialize_env_value(new_value)
        write_env_file(env_values)
        # on windows:
        if platform.system() == "Windows":
            set_user_env_vars({env_key: env_values[env_key]})

    def _serialize_env_value(self, value: Any) -> str:
        """Normalize values for env files."""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)


class ConfigTab:
    """Tab that lists and edits runtime configuration."""

    def __init__(self, tab: Tab) -> None:
        with ui.tab_panel(tab):
            ui.label(t.config_header).classes(f"text-xl my-2 {Styles.SUBHEADER}")
            ui.label(t.config_description).classes("text-app-secondary mb-4")
            with ui.card().classes(f"{Styles.CARD} w-full p-4 flex flex-col gap-1"):
                for field in CONFIG_FIELDS:
                    ConfigFieldRow(cfg, field)


def build_config_tab(tab: Tab) -> ConfigTab:
    return ConfigTab(tab)
