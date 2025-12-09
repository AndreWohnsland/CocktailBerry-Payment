import time

import streamlit as st

from src.frontend.data import api_client

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
NFC_SCAN_ITERATIONS = 20  # 0.5s each = 10 seconds total
NFC_SCAN_DELAY = 0.5


def _scan_nfc_card() -> str | None:
    """Scan NFC card with spinner."""
    with st.spinner("Waiting for NFC card..."):
        for _ in range(NFC_SCAN_ITERATIONS):
            nfc_id = api_client.fetch_nfc_id()
            if nfc_id:
                st.success(f"✅ Card scanned: {nfc_id}")
                return nfc_id
            time.sleep(NFC_SCAN_DELAY)
        st.error("No card detected. Please try again.")
        return None


def _create_user_view() -> None:
    """View for creating a new user."""
    st.subheader("Create New User")

    if st.button("🔍 Scan NFC Card", key="create_scan"):
        nfc_id = _scan_nfc_card()
        if nfc_id:
            st.session_state.scanned_nfc = nfc_id

    if "scanned_nfc" in st.session_state:
        st.info(f"Scanned NFC ID: {st.session_state.scanned_nfc}")

        existing_user = api_client.get_user(st.session_state.scanned_nfc)
        if existing_user:
            st.warning(f"User already exists: {existing_user['name']}")
        else:
            name = st.text_input("Name")
            is_adult = st.checkbox("Is 18 or older")

            if st.button("Create User"):
                if name:
                    result = api_client.create_user(st.session_state.scanned_nfc, name, is_adult)
                    if result:
                        st.success(f"✅ User created: {result['name']}")
                        del st.session_state.scanned_nfc
                        st.rerun()
                    else:
                        st.error("Failed to create user")
                else:
                    st.error("Please enter a name")


def _edit_user_view() -> None:
    """View for editing an existing user."""
    st.subheader("Edit User")

    if st.button("🔍 Scan NFC Card", key="edit_scan"):
        nfc_id = _scan_nfc_card()
        if nfc_id:
            st.session_state.edit_nfc = nfc_id

    if "edit_nfc" in st.session_state:
        user = api_client.get_user(st.session_state.edit_nfc)
        if user:
            st.info(f"Editing user: {user['name']}")
            new_name = st.text_input("Name", value=user["name"])
            new_is_adult = st.checkbox("Is 18 or older", value=user["is_adult"])

            if st.button("Update User"):
                result = api_client.update_user(st.session_state.edit_nfc, new_name, new_is_adult)
                if result:
                    st.success(f"✅ User updated: {result['name']}")
                    del st.session_state.edit_nfc
                    st.rerun()
                else:
                    st.error("Failed to update user")
        else:
            st.error("User not found")


def _delete_user_view() -> None:
    """View for deleting a user."""
    st.subheader("Delete User")

    if st.button("🔍 Scan NFC Card", key="delete_scan"):
        nfc_id = _scan_nfc_card()
        if nfc_id:
            st.session_state.delete_nfc = nfc_id

    if "delete_nfc" in st.session_state:
        user = api_client.get_user(st.session_state.delete_nfc)
        if user:
            st.warning(f"Are you sure you want to delete user: {user['name']}?")
            col1, col2 = st.columns(2)
            if col1.button("Yes, Delete"):
                if api_client.delete_user(st.session_state.delete_nfc):
                    st.success("✅ User deleted")
                    del st.session_state.delete_nfc
                    st.rerun()
                else:
                    st.error("Failed to delete user")
            if col2.button("Cancel"):
                del st.session_state.delete_nfc
                st.rerun()
        else:
            st.error("User not found")


def _view_all_users() -> None:
    """View for listing all users."""
    st.subheader("All Users")
    users = api_client.list_users()
    if users:
        for user in users:
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"**{user['name']}**")
            col2.write(f"NFC: {user['nfc_id']}")
            col3.write(f"Balance: €{user['balance']:.2f}")
            col4.write("🔞 Adult" if user["is_adult"] else "👶 Minor")
    else:
        st.info("No users found")


def user_management_tab() -> None:
    """User management interface."""
    st.header("👤 User Management")

    action = st.radio("Select Action", ["Create User", "Edit User", "Delete User", "View All Users"], horizontal=True)

    if action == "View All Users":
        _view_all_users()
    elif action == "Create User":
        _create_user_view()
    elif action == "Edit User":
        _edit_user_view()
    elif action == "Delete User":
        _delete_user_view()


def balance_topup_tab() -> None:
    """Balance top-up interface."""
    st.header("💰 Balance Top-Up")

    st.subheader("Scan Card")
    if st.button("🔍 Scan NFC Card", key="topup_scan"):
        nfc_id = _scan_nfc_card()
        if nfc_id:
            st.session_state.topup_nfc = nfc_id

    if "topup_nfc" in st.session_state:
        user = api_client.get_user(st.session_state.topup_nfc)
        if user:
            st.info(f"**User:** {user['name']}")
            st.metric("Current Balance", f"€{user['balance']:.2f}")

            st.subheader("Update Balance")
            amount = st.number_input(
                "Amount (negative to subtract)",
                min_value=-1000.0,
                max_value=1000.0,
                value=10.0,
                step=0.50,
            )

            if st.button("Update Balance"):
                result = api_client.update_balance(st.session_state.topup_nfc, amount)
                if result:
                    st.success(f"✅ New balance: €{result['balance']:.2f}")
                    st.rerun()
                else:
                    st.error("Failed to update balance")

            if st.button("Clear"):
                del st.session_state.topup_nfc
                st.rerun()
        else:
            st.error("User not found. Please create the user first.")
