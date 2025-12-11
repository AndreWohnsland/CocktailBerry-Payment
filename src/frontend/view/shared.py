"""Shared components and utilities for the frontend views."""

import streamlit as st

from ..constants import NFC_SCAN_TIMEOUT
from ..core.nfc import nfc_scanner
from ..data import api_client


@st.cache_data(ttl=120)
def fetch_users() -> list[dict]:
    """Fetch users with short-lived cache to prevent redundant API calls."""
    return api_client.list_users()


def invalidate_user_cache() -> None:
    """Clear the users cache to force a refresh."""
    fetch_users.clear()


def scan_nfc_card() -> str | None:
    """Scan NFC card with spinner (one-shot mode).

    Returns:
        The NFC ID if a card was scanned, None otherwise.

    """
    if not nfc_scanner.is_available():
        st.error("NFC reader not available")
        return None

    with st.spinner("Waiting for NFC card..."):
        nfc_id = nfc_scanner.one_shot(timeout=NFC_SCAN_TIMEOUT)
        if nfc_id:
            st.success(f"✅ Card scanned: {nfc_id}")
            return nfc_id
        st.error("No card detected. Please try again.")
        return None
