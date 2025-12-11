"""Balance top-up tab view."""

import streamlit as st

from ..constants import MAX_BALANCE, MIN_BALANCE
from ..data import api_client
from .shared import invalidate_user_cache, scan_nfc_card


def balance_topup_tab() -> None:
    """Balance top-up interface."""
    st.header("💰 Balance Top-Up")

    if st.button("🔍 Scan NFC Card", key="topup_scan"):
        nfc_id = scan_nfc_card()
        if nfc_id:
            st.session_state.topup_nfc = nfc_id

    if "topup_nfc" not in st.session_state:
        return

    nfc_id = st.session_state.topup_nfc
    if not isinstance(nfc_id, str):
        return

    user = api_client.get_user(nfc_id)

    if not user:
        st.error(f"Chip `{nfc_id}` not found. Register it first.")
        if st.button("Clear", key="topup_clear"):
            del st.session_state.topup_nfc
            st.rerun()
        return

    st.metric("Current Balance", f"€{user['balance']:.2f}")

    amount = st.number_input(
        "Amount to add (negative to subtract)",
        min_value=MIN_BALANCE,
        max_value=MAX_BALANCE,
        value=10.0,
        step=0.50,
        key="topup_amount",
    )

    col1, col2 = st.columns(2)
    if col1.button("💳 Update Balance", key="topup_submit", type="primary"):
        result = api_client.update_balance(nfc_id, amount)
        if result:
            st.success(f"✅ New balance: €{result['balance']:.2f}")
            invalidate_user_cache()
            st.rerun()
        else:
            st.error("Failed to update balance")

    if col2.button("🔄 Scan Another", key="topup_another"):
        del st.session_state.topup_nfc
        st.rerun()
