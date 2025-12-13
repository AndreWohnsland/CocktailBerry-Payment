# components/amount_selector.py
"""Reusable amount selector component for NiceGUI."""

from collections.abc import Callable

from nicegui import ui


class AmountSelector:
    """A reusable component for selecting monetary amounts.

    Provides preset amount buttons and increment/decrement controls.
    """

    def __init__(
        self,
        initial_value: float = 10.0,
        min_value: float = 0.0,
        max_value: float = 1000.0,
        preset_amounts: list[int] | None = None,
        step_amounts: list[int] | None = None,
        on_change: Callable[[float], None] | None = None,
        show_sign: bool = True,
    ) -> None:
        """Initialize the AmountSelector component.

        Args:
            initial_value: Starting amount value.
            min_value: Minimum allowable amount.
            max_value: Maximum allowable amount.
            preset_amounts: List of preset amounts for quick selection (default: [5, 10, 20, 50]).
            step_amounts: List of step values for increment/decrement (default: [-5, -1, 1, 5]).
            on_change: Optional callback when amount changes.
            show_sign: Whether to show +/- sign in the display (default: True).

        """
        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._preset_amounts = preset_amounts or [5, 10, 20, 50]
        self._step_amounts = step_amounts or [-5, -1, 1, 5]
        self._on_change = on_change
        self._show_sign = show_sign

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the selector UI elements."""
        # Preset amount buttons
        with ui.grid(columns=2).classes("w-full max-w-md gap-3"):
            for amount in self._preset_amounts:
                ui.button(f"€ {amount}").classes("py-4 flex-1 text-xl").on_click(
                    lambda a=amount: self.set_value(a)  # type: ignore
                )

        # Current amount display
        self._amount_label = ui.label(self._format_display()).classes(
            "text-5xl my-2 font-bold text-center bg-surface rounded-lg px-6 py-4 w-full max-w-md"
        )

        # Increment/decrement buttons
        with ui.grid(columns=len(self._step_amounts)).classes("w-full max-w-md gap-2"):
            for step in self._step_amounts:
                icon = "remove" if step < 0 else "add"
                ui.button(f"€ {abs(step)}", icon=icon).classes("py-3 text-lg opacity-85").on_click(
                    lambda s=step: self.change_value(s)  # type: ignore
                )

    def _format_display(self) -> str:
        """Format the amount for display."""
        sign = ""
        if self._value > 0 and self._show_sign:
            sign = "+ "
        elif self._value < 0 and self._show_sign:
            sign = "- "
        return f"{sign}€ {abs(self._value):.2f}"

    def _refresh_display(self) -> None:
        """Update the visible amount label and trigger callback."""
        self._amount_label.text = self._format_display()
        if self._on_change:
            self._on_change(self._value)

    @property
    def value(self) -> float:
        """Get the current amount value."""
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        """Set the amount value."""
        self._value = new_value
        self._refresh_display()

    def set_value(self, amount: float) -> None:
        """Set the amount to a specific value."""
        self._value = amount
        self._refresh_display()

    def change_value(self, delta: float) -> None:
        """Change the amount by a delta value, limit between min and max."""
        new_value = self._value + delta
        if new_value < self._min_value:
            new_value = self._min_value
        elif new_value > self._max_value:
            new_value = self._max_value
        self._value = new_value
        self._refresh_display()

    def reset(self, value: float = 10.0) -> None:
        """Reset the selector to a specific value."""
        self._value = value
        self._refresh_display()
