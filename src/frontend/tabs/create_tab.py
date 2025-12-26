from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.components import AmountSelector, NfcScannerSection
from src.frontend.core.config import config as cfg
from src.frontend.i18n.translator import translations as t
from src.frontend.services import NFCService, is_err
from src.frontend.theme import Styles


class CreateTab:
    """Create tab: scan NFC, set options, create user."""

    def __init__(self, service: NFCService, tab: Tab) -> None:
        self.service = service
        self._scan_hint = t.nfc_simulate_hint if self.service.mock_nfc_enabled else t.nfc_scan_hint

        with ui.tab_panel(tab):
            ui.label(t.header_create).classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.nfc_scanner = NfcScannerSection(
                scan_hint=self._scan_hint,
                on_scan=self._perform_scan,
                on_clear=self._on_clear,
                on_scan_complete=self._on_scan_complete,
            )
            self.creation_container = ui.column().classes("w-full")
            with self.creation_container:
                with ui.card().classes(f"{Styles.CARD} w-full p-4 pb-6 flex flex-col items-center gap-3"):
                    self.checkbox_adult = (
                        ui.checkbox(t.create_adult_description, value=True)
                        .classes("self-center mb-2 text-lg")
                        .props("size=xl")
                    )
                    self.amount_selector = AmountSelector(show_sign=False, preset_amounts=[0, 5, 10, 20, 50, 100])
                    self.save_button = ui.button(t.create_nfc, icon="save", color="secondary").classes(
                        "py-3 mt-8 w-full max-w-md text-xl font-bold"
                    )

                with ui.card().classes(f"{Styles.CARD} w-full p-2 flex flex-col items-center gap-3"):
                    self.checkbox_overwrite = (
                        ui.switch(t.create_overwrite_description, value=False, on_change=self.choose_create_button_text)
                        .classes("self-center text-lg")
                        .props("size=xl color=negative")
                    ).on_value_change(self.choose_create_button_text)

        self.creation_container.visible = False
        self.save_button.on_click(self.save_user)

    async def choose_create_button_text(self) -> None:
        """Set the text to create/overwrite."""
        if self.checkbox_overwrite.value:
            self.save_button.set_text(t.overwrite_nfc)
        else:
            self.save_button.set_text(t.create_nfc)

    async def _perform_scan(self) -> str | None:
        """Perform the actual NFC scan."""
        self.save_button.disable()
        self.creation_container.visible = False
        return await self.service.nfc.one_shot()

    def _on_scan_complete(self, nfc_id: str | None) -> None:
        """Handle scan completion."""
        if not nfc_id:
            ui.notify(t.nfc_timeout, type="warning", position="top-right")
            return

        self.checkbox_adult.value = True
        self.amount_selector.reset(cfg.default_balance)
        self.creation_container.visible = True
        self.save_button.enable()

    def _on_clear(self) -> None:
        """Handle clear button press."""
        self.creation_container.visible = False

    async def save_user(self) -> None:
        """Send to backend (mock) and add to store."""
        if not self.nfc_scanner.nfc_id:
            # should not happen due to UI state, but just in case
            ui.notify("No card scanned yet!", type="negative", position="top-right")
            return

        self.save_button.disable()
        self.nfc_scanner.set_status(t.create_nfc_creating)

        service_function = self.service.create_nfc if not self.checkbox_overwrite.value else self.service.update_nfc
        result = await service_function(
            nfc_id=self.nfc_scanner.nfc_id,
            is_adult=self.checkbox_adult.value,
            balance=self.amount_selector.value,
        )
        if is_err(result):
            self.nfc_scanner.set_status(result.error)
            ui.notify(result.error, type="negative", position="top-right")
            self.save_button.enable()
            return

        self.nfc_scanner.set_status(t.create_nfc_saved)
        ui.notify(t.create_nfc_saved, type="positive", position="top-right")
        self.reset_ui()

    def reset_ui(self) -> None:
        """Reset the Create tab UI state."""
        self.nfc_scanner.reset()
        self.creation_container.visible = False
        self.checkbox_overwrite.value = False


def build_create_tab(tab: Tab, service: NFCService) -> CreateTab:
    return CreateTab(service, tab)
