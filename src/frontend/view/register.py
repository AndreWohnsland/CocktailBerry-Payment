"""Register chip tab view."""

import streamlit as st

from ..data import api_client
from .shared import invalidate_user_cache, scan_nfc_card


def register_chip_tab() -> None:
    """Register new NFC chip interface."""
    st.header("➕ Register New Chip")  # noqa: RUF001

    # Step 1: Scan NFC
    st.subheader("1. Scan NFC Chip")
    if st.button("🔍 Scan NFC Card", key="register_scan"):
        nfc_id = scan_nfc_card()
        if nfc_id:
            st.session_state.register_nfc = nfc_id
            # Check if already exists
            existing = api_client.get_user(nfc_id)
            st.session_state.register_exists = existing is not None

    # Step 2: Show result and create form
    if "register_nfc" in st.session_state:
        _render_register_form()


def _render_register_form() -> None:
    """Render the registration form after scanning."""
    nfc_id = st.session_state.register_nfc

    if st.session_state.get("register_exists"):
        st.warning(f"⚠️ Chip `{nfc_id}` is already registered!")
        if st.button("Clear", key="register_clear"):
            _clear_register_state()
            st.rerun()
        return

    st.info(f"📝 Registering chip: `{nfc_id}`")

    st.subheader("2. Set Properties")
    is_adult = st.checkbox("Is 18 or older", key="register_adult")

    col1, col2 = st.columns(2)
    if col1.button("✅ Register Chip", key="register_submit", type="primary"):
        result = api_client.create_user(nfc_id, is_adult)
        if result:
            st.success(f"✅ Chip registered! Balance: €{result['balance']:.2f}")
            invalidate_user_cache()
            _clear_register_state()
            st.rerun()
        else:
            st.error("Failed to register chip")

    if col2.button("❌ Cancel", key="register_cancel"):
        _clear_register_state()
        st.rerun()


def _clear_register_state() -> None:
    """Clear registration session state."""
    if "register_nfc" in st.session_state:
        del st.session_state.register_nfc
    if "register_exists" in st.session_state:
        del st.session_state.register_exists
