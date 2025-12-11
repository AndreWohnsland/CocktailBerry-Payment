"""Manage chips tab view."""

import streamlit as st

from ..data import api_client
from .shared import fetch_users, invalidate_user_cache

COLS_LAYOUT = [2, 2, 1, 1]


def manage_chips_tab() -> None:
    """Manage existing NFC chips - list, edit, delete."""
    st.header("📋 Manage Chips")

    # Initialize edit state
    if "editing_nfc" not in st.session_state:
        st.session_state.editing_nfc = None

    # Filter input
    filter_text = st.text_input("🔍 Filter by NFC ID", key="chip_filter", placeholder="Enter NFC ID to filter...")

    # Fetch users with caching
    users = fetch_users()

    # Apply filter
    if filter_text:
        users = [u for u in users if filter_text.lower() in u["nfc_id"].lower()]

    if not users:
        st.info("No chips found" + (" matching filter" if filter_text else ""))
        return

    # Table header
    cols = st.columns(COLS_LAYOUT)
    cols[0].markdown("**NFC ID**")
    cols[1].markdown("**Balance**")
    cols[2].markdown("**Adult**")
    cols[3].markdown("**Delete**")

    st.divider()

    for user in users:
        _render_display_row(user)


def _render_display_row(user: dict) -> None:
    """Render a user row in display mode."""
    nfc_id = user["nfc_id"]
    cols = st.columns(COLS_LAYOUT)

    cols[0].write(nfc_id)
    cols[1].write(f"€{user['balance']:.2f}")
    cols[2].write("✅" if user["is_adult"] else "❌")

    if cols[3].button("🗑️", key=f"del_{nfc_id}", help="Delete"):
        st.session_state.deleting_nfc = nfc_id
        st.rerun()

    # Delete confirmation
    if st.session_state.get("deleting_nfc") == nfc_id:
        st.warning(f"Delete chip `{nfc_id}`?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, Delete", key=f"confirm_del_{nfc_id}", type="primary"):
            if api_client.delete_user(nfc_id):
                st.success("Deleted!")
                invalidate_user_cache()
                del st.session_state.deleting_nfc
                st.rerun()
            else:
                st.error("Failed to delete")
        if c2.button("Cancel", key=f"cancel_del_{nfc_id}"):
            del st.session_state.deleting_nfc
            st.rerun()
