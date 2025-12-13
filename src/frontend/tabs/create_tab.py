from nicegui import ui
from nicegui.elements.tabs import Tab

from src.frontend.components import AmountSelector, NfcScannerSection
from src.frontend.core.config import config as cfg
from src.frontend.i18n.translator import translations as t
from src.frontend.services import NFCService, mock_post_to_backend
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

            self.form_card = ui.card().classes(f"{Styles.CARD} w-full mb-4 p-4 pb-6 flex flex-col items-center gap-3")
            self.form_card.visible = False
            with self.form_card:
                self.checkbox_adult = (
                    ui.checkbox(t.create_adult_description, value=True)
                    .classes("self-center mb-2 text-lg")
                    .props("size=xl")
                )
                self.amount_selector = AmountSelector(show_sign=False, preset_amounts=[0, 5, 10, 20, 50, 100])

                self.save_button = ui.button(t.create_nfc, icon="save", color="secondary").classes(
                    "py-3 mt-8 w-full max-w-md text-xl font-bold"
                )

        # Attach handlers
        self.save_button.on_click(self.save_user)

    # --- UI handlers -------------------------------------------------

    async def _perform_scan(self) -> str | None:
        """Perform the actual NFC scan."""
        self.save_button.disable()
        self.form_card.visible = False
        return await self.service.nfc.one_shot()

    def _on_scan_complete(self, nfc_id: str | None) -> None:
        """Handle scan completion."""
        if not nfc_id:
            return

        self.checkbox_adult.value = True
        self.amount_selector.reset(cfg.default_balance)
        self.form_card.visible = True
        self.save_button.enable()

    def _on_clear(self) -> None:
        """Handle clear button press."""
        self.form_card.visible = False

    async def save_user(self) -> None:
        """Send to backend (mock) and add to store."""
        if not self.nfc_scanner.nfc_id:
            # should not happen due to UI state, but just in case
            ui.notify("No card scanned yet!", type="negative", position="top-right")
            return

        self.save_button.disable()
        self.nfc_scanner.set_status(t.create_nfc_creating)

        # TODO: this will be the service (currently store)
        await mock_post_to_backend(
            {
                "nfc_id": self.nfc_scanner.nfc_id,
                "is_adult": self.checkbox_adult.value,
                "balance": self.amount_selector.value,
            }
        )

        self.service.create_nfc(
            nfc_id=self.nfc_scanner.nfc_id,
            is_adult=self.checkbox_adult.value,
            balance=self.amount_selector.value,
        )
        self.nfc_scanner.set_status(t.create_nfc_saved)
        ui.notify(t.create_nfc_saved, type="positive", position="top-right")
        self.reset_ui()

    def reset_ui(self) -> None:
        """Reset the Create tab UI state."""
        self.nfc_scanner.reset()
        self.form_card.visible = False


def build_create_tab(tab: Tab, service: NFCService) -> CreateTab:
    return CreateTab(service, tab)
