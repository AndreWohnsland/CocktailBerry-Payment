"""Reusable NFC search/filter bar for NiceGUI.

A text input with a scan-to-fill button and a clear button. Behavior-agnostic: it
exposes the value (and the underlying input, for binding) and fires `on_change` on
value changes. Typing is debounced via the input's Quasar `debounce` prop; a scan
fills the value with the change-handler suppressed and then fires `on_change`
immediately — so the debounce applies to typing only, never to a scan.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from nicegui import ui

from src.frontend.i18n.translator import translations as t


class NfcSearchBar:
    """An NFC-id input with scan-to-fill and clear buttons; emits `on_change(value)`."""

    def __init__(
        self,
        hint: str,
        on_scan: Callable[[], Awaitable[str | None]],
        on_change: Callable[[str], Any] | None = None,
        debounce_ms: int = 0,
    ) -> None:
        self._on_scan = on_scan
        self._on_change = on_change
        self._suppress = False

        with ui.row().classes("items-center w-full mb-2"):
            self.input = ui.input(hint, on_change=self._handle_change).classes("flex-grow")
            if debounce_ms > 0:
                self.input.props(f"debounce={debounce_ms}")
            self.scan_button = ui.button(t.nfc_scan, icon="nfc", color="primary").classes("py-2").on_click(self._scan)
            self.clear_button = ui.button(t.clear, icon="clear", color="neutral").classes("py-2").on_click(self._clear)

    @property
    def value(self) -> str:
        """Current input text, trimmed."""
        return (self.input.value or "").strip()

    def _handle_change(self) -> None:
        """Fire `on_change` for user typing (debounced by the input). Suppressed during a scan."""
        if self._suppress or self._on_change is None:
            return
        self._on_change(self.value)

    async def _scan(self) -> None:
        """Scan a card, fill the input, and fire `on_change` immediately (bypassing the debounce)."""
        self.scan_button.props("loading")
        self.scan_button.disable()
        self.input.disable()
        try:
            nfc_id = await self._on_scan()
        finally:
            self.scan_button.props(remove="loading")
            self.scan_button.enable()
            self.input.enable()

        if not nfc_id:
            ui.notify(t.nfc_timeout, type="warning", position="top-right")
            return

        # Set the value with the typing path suppressed (NiceGUI invokes the change
        # handler synchronously on assignment), then fire on_change explicitly — so
        # a scan searches at once instead of waiting out the debounce.
        self._suppress = True
        self.input.value = nfc_id
        self._suppress = False
        if self._on_change is not None:
            self._on_change(self.value)

    def _clear(self) -> None:
        """Clear the input; the resulting change fires `on_change` so consumers can reset."""
        self.input.value = ""
