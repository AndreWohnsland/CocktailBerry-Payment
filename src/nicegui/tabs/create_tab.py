# tabs/create_tab.py

from services import mock_post_to_backend
from store import UserStore
from theme import Styles

from nicegui import ui


class CreateTab:
    """Create tab: scan NFC, set options, create user."""

    def __init__(self, store: UserStore, tab) -> None:
        self.store = store
        self.card_id: str | None = None

        with ui.tab_panel(tab):
            ui.label("Create user via NFC scan").classes(f"text-xl my-2 {Styles.SUBHEADER}")

            self.status_label = ui.label("Ready to scan").classes(Styles.TEXT_SECONDARY)
            with ui.row().classes("items-center mb-4"):
                self.scan_button = ui.button("Scan NFC card", icon="nfc", color="primary").classes("py-2")
                self.card_label = ui.label("No card scanned yet").classes(f"text-sm {Styles.TEXT_MUTED}")

            self.checkbox_adult = ui.checkbox("Adult")
            self.checkbox_adult.visible = False

            self.balance_input = ui.number(label="Initial Balance (€)", value=10.0, format="%.2f", step=1).classes(
                "w-48"
            )
            self.balance_input.visible = False

            self.save_button = ui.button("Create Card", icon="save", color="secondary").classes("my-4 py-4")

            self.save_button.visible = False

        # Attach handlers
        self.scan_button.on_click(self.start_scan)
        self.save_button.on_click(self.save_user)

    # --- UI handlers -------------------------------------------------

    async def start_scan(self):
        """Start NFC scan (mocked)."""
        self.scan_button.disable()
        self.save_button.disable()

        self.status_label.text = "Scanning NFC card..."
        self.card_label.text = "Hold a card to the reader (mock, 5 seconds)..."

        self.checkbox_adult.visible = False
        self.save_button.visible = False
        self.card_id = None

        card_id = await self.store.nfc.one_shot(timeout=10.0, poll_interval=0.5)

        self.card_id = card_id
        self.card_label.text = f"Scanned card ID: {card_id}"
        self.status_label.text = "Scan complete"
        self.scan_button.enable()
        if not card_id:
            return

        self.checkbox_adult.value = False
        self.checkbox_adult.visible = True

        self.balance_input.value = 10.0
        self.balance_input.visible = True

        self.save_button.visible = True
        self.save_button.enable()

    async def save_user(self):
        """Send to backend (mock) and add to store."""
        if not self.card_id:
            ui.notify("No card scanned yet!", color="negative", position="top-right")
            return

        self.save_button.disable()
        self.status_label.text = "Sending data to backend..."

        user_data = {
            "card_id": self.card_id,
            "adult": self.checkbox_adult.value,
            "balance": self.balance_input.value or 10.0,
        }

        await mock_post_to_backend(user_data)

        self.store.add_user(user_data)

        self.status_label.text = "User saved successfully!"
        ui.notify("Card saved successfully.", color="positive", position="top-right")
        self.reset_ui()

    def reset_ui(self):
        """Reset the Create tab UI state."""
        self.status_label.text = "Ready to scan"
        self.card_label.text = "No card scanned yet"
        self.checkbox_adult.visible = False
        self.balance_input.visible = False
        self.save_button.visible = False
        self.card_id = None


def build_create_tab(tab, store: UserStore) -> CreateTab:
    """Helper to construct the CreateTab."""
    return CreateTab(store, tab)
