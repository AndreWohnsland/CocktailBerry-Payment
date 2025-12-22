from nicegui import ui

# =============================================================================
# COLOR PALETTE
# =============================================================================
# Define your brand colors here. Change these values to customize the theme.

COLORS = {
    # Primary brand color - used for main actions, highlights
    "primary": "#39489e",  # Indigo
    # Secondary brand color - used for secondary actions
    "secondary": "#ff2866",  # Pink
    # Neutral color - used for less prominent elements
    "neutral": "#90a4ae",  # Blue Gray (lighter)
    # Accent color - for special highlights
    "accent": "#ff7043",  # Deep Orange
    # Background colors (dark mode)
    "background": "#121212",  # Dark background
    "surface": "#1e1e1e",  # Card/surface background (slightly lighter)
    "surface_elevated": "#2d2d2d",  # Elevated surfaces (dialogs, menus)
    # Text colors (light for dark mode)
    "text_primary": "#ffffff",  # Main text (white)
    "text_secondary": "#b0b0b0",  # Secondary text (light gray)
    "text_muted": "#757575",  # Muted/disabled text (medium gray)
    # Semantic colors (slightly brighter for dark mode)
    "positive": "#66bb6a",  # Success/positive actions
    "negative": "#ef5350",  # Error/destructive actions
    "warning": "#ffb74d",  # Warning states
    "info": "#42a5f5",  # Informational
    # Dark mode colors for Quasar
    "dark": "#1e1e1e",
    "dark_page": "#121212",
}


# =============================================================================
# CSS CLASS DEFINITIONS
# =============================================================================
# Custom CSS classes that use our color palette


def get_custom_css() -> str:
    """Generate custom CSS using our color palette."""
    return f"""
    :root {{
        --color-primary: {COLORS["primary"]};
        --color-secondary: {COLORS["secondary"]};
        --color-neutral: {COLORS["neutral"]};
        --color-accent: {COLORS["accent"]};
        --color-background: {COLORS["background"]};
        --color-surface: {COLORS["surface"]};
        --color-surface-elevated: {COLORS["surface_elevated"]};
        --color-text-primary: {COLORS["text_primary"]};
        --color-text-secondary: {COLORS["text_secondary"]};
        --color-text-muted: {COLORS["text_muted"]};
    }}

    /* Background utility classes */
    .bg-app {{ background-color: {COLORS["background"]} !important; }}
    .bg-surface {{ background-color: {COLORS["surface"]} !important; }}
    .bg-surface-elevated {{ background-color: {COLORS["surface_elevated"]} !important; }}
    .bg-primary {{ background-color: {COLORS["primary"]} !important; }}
    .bg-secondary {{ background-color: {COLORS["secondary"]} !important; }}
    .bg-neutral {{ background-color: {COLORS["neutral"]} !important; }}

    /* Text utility classes */
    .text-app-primary {{ color: {COLORS["text_primary"]} !important; }}
    .text-app-secondary {{ color: {COLORS["text_secondary"]} !important; }}
    .text-app-muted {{ color: {COLORS["text_muted"]} !important; }}
    .text-on-primary {{ color: white !important; }}
    .text-on-secondary {{ color: white !important; }}

    /* Border utility classes */
    .border-primary {{ border-color: {COLORS["primary"]} !important; }}
    .border-secondary {{ border-color: {COLORS["secondary"]} !important; }}
    .border-neutral {{ border-color: {COLORS["neutral"]} !important; }}

    /* Dark mode overrides for Quasar components */
    .q-card, .q-dialog__inner > div {{
        background-color: {COLORS["surface_elevated"]} !important;
        color: {COLORS["text_primary"]} !important;
    }}

    .q-tab-panels {{
        background-color: {COLORS["surface"]} !important;
    }}

    .q-tab-panel {{
        color: {COLORS["text_primary"]} !important;
    }}

    .q-field__control {{
        color: {COLORS["text_primary"]} !important;
    }}

    .q-field__label {{
        color: {COLORS["text_secondary"]} !important;
    }}

    .q-input, .q-field__native {{
        color: {COLORS["text_primary"]} !important;
    }}
    """


# =============================================================================
# THEME APPLICATION
# =============================================================================


def apply_theme() -> None:
    """Apply the theme to the NiceGUI app."""
    # Enable dark mode
    ui.dark_mode(True)

    # Set Quasar's built-in color system
    ui.colors(
        primary=COLORS["primary"],
        secondary=COLORS["secondary"],
        accent=COLORS["accent"],
        positive=COLORS["positive"],
        negative=COLORS["negative"],
        warning=COLORS["warning"],
        info=COLORS["info"],
        dark=COLORS["dark"],
        dark_page=COLORS["dark_page"],
    )

    # Add custom CSS for additional styling options
    ui.add_css(get_custom_css())

    # Style the body background
    ui.query("body").classes("bg-app")


def apply_page_background() -> None:
    """Apply background styling to the current page."""
    ui.query("body").style(f"background-color: {COLORS['background']}")


# =============================================================================
# STYLE HELPERS
# =============================================================================
# Convenience functions for consistent styling across components


class Styles:
    """Pre-defined style class combinations for common UI patterns."""

    # Headers and titles
    HEADER = "text-app-primary font-bold"
    SUBHEADER = "text-app-secondary font-semibold"

    # Body text
    TEXT = "text-app-primary"
    TEXT_SECONDARY = "text-app-secondary"
    TEXT_MUTED = "text-app-muted"

    # Cards and containers
    CARD = "bg-surface shadow-md rounded-lg"

    # Buttons (use with color prop for Quasar colors)
    BUTTON_PRIMARY = ""  # Use color="primary" prop
    BUTTON_SECONDARY = ""  # Use color="secondary" prop

    # Status indicators
    STATUS_SUCCESS = "text-positive"
    STATUS_ERROR = "text-negative"
    STATUS_WARNING = "text-warning"
    STATUS_INFO = "text-info"
