import streamlit as st

from src.frontend.view.manage import manage_chips_tab
from src.frontend.view.register import register_chip_tab
from src.frontend.view.topup import balance_topup_tab

st.set_page_config(
    page_title="CocktailBerry Payment",
    page_icon="🍹",
    layout="centered",
)

st.title("🍹 CocktailBerry Payment Management")

# Create tabs
tab1, tab2, tab3 = st.tabs(["➕ Register Chip", "📋 Manage Chips", "💰 Balance Top-Up"])  # noqa: RUF001

with tab1:
    register_chip_tab()

with tab2:
    manage_chips_tab()

with tab3:
    balance_topup_tab()
