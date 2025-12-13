"""Reusable NFC scanner section component for NiceGUI."""

from collections.abc import Awaitable, Callable

from nicegui import ui

from src.frontend.i18n.translator import translations as t
from src.frontend.theme import Styles


class NfcScannerSection:
    """A reusable component for NFC scanning UI.

    Provides status label, scan button, clear button, and card label.
    """

    def __init__(
        self,
        scan_hint: str,
        on_scan: Callable[[], Awaitable[str | None]],
        on_clear: Callable[[], None] | None = None,
        on_scan_complete: Callable[[str | None], None] | None = None,
    ) -> None:
        """Initialize the NfcScannerSection component.

        Args:
            scan_hint: Text to show while scanning (e.g., "Hold a card...").
            on_scan: Async callback that performs the actual NFC scan and returns nfc_id.
            on_clear: Optional callback when clear button is pressed.
            on_scan_complete: Optional callback when scan completes with the nfc_id result.

        """
        self._scan_hint = scan_hint
        self._on_scan = on_scan
        self._on_clear = on_clear
        self._on_scan_complete = on_scan_complete
        self._nfc_id: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the scanner UI elements."""
        self.status_label = ui.label(t.nfc_ready_to_scan).classes(Styles.TEXT_SECONDARY)
        with ui.row().classes("items-center mb-4 gap-2"):
            self.scan_button = ui.button(t.nfc_scan, icon="nfc", color="primary").classes("py-2")
            self.clear_button = ui.button(t.clear, icon="clear", color="standard").classes("py-2").props("flat")
            self.clear_button.visible = False
            self.card_label = ui.label(t.nfc_no_card_scanned).classes(f"text-sm {Styles.TEXT_MUTED} text-center")

        # Attach handlers
        self.scan_button.on_click(self._start_scan)
        self.clear_button.on_click(self._clear_scan)

    @property
    def nfc_id(self) -> str | None:
        """Return the currently scanned card ID."""
        return self._nfc_id

    async def _start_scan(self) -> None:
        """Start NFC scan using the configured callback."""
        self.scan_button.disable()
        self.clear_button.visible = False

        self.status_label.text = t.nfc_scanning_progress
        self.card_label.text = self._scan_hint

        self._nfc_id = None

        nfc_id = await self._on_scan()
        self._nfc_id = nfc_id

        if nfc_id:
            self.card_label.text = t.nfc_scanned_card.format(nfc_id=nfc_id)
            self.status_label.text = t.nfc_scan_complete
            self.clear_button.visible = True
        else:
            self.card_label.text = t.nfc_no_card_detected
            self.status_label.text = t.nfc_timeout

        self.scan_button.enable()

        if self._on_scan_complete:
            self._on_scan_complete(nfc_id)

    def _clear_scan(self) -> None:
        """Clear the current scan and reset UI."""
        self._nfc_id = None
        self.status_label.text = t.nfc_ready_to_scan
        self.card_label.text = t.nfc_no_card_scanned
        self.clear_button.visible = False

        if self._on_clear:
            self._on_clear()

    def set_status(self, text: str) -> None:
        """Update the status label text."""
        self.status_label.text = text

    def set_card_label(self, text: str) -> None:
        """Update the card label text."""
        self.card_label.text = text

    def reset(self) -> None:
        """Reset the scanner section to initial state."""
        self._nfc_id = None
        self.status_label.text = t.nfc_ready_to_scan
        self.card_label.text = t.nfc_no_card_scanned
        self.clear_button.visible = False
        self.scan_button.enable()

    def disable_scan(self) -> None:
        """Disable the scan button."""
        self.scan_button.disable()

    def enable_scan(self) -> None:
        """Enable the scan button."""
        self.scan_button.enable()
