import streamlit as st

from src.frontend.view.components import balance_topup_tab, user_management_tab

st.set_page_config(
    page_title="CocktailBerry Payment",
    page_icon="🍹",
    layout="wide",
)

st.title("🍹 CocktailBerry Payment Management")

# Create tabs
tab1, tab2 = st.tabs(["👤 User Management", "💰 Balance Top-Up"])

with tab1:
    user_management_tab()

with tab2:
    balance_topup_tab()
