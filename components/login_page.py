"""
Login Page Component for MAHSR-T3-DPR-App
End-to-end authenticated login flow for:
- Site Engineer (name + site)
- Project Manager (username + password)
- Admin (username + password)

Supabase Role Mapping:
- Admin → Admin Dashboard
- Administrator → PM Dashboard
- admin → Site Engineer Dashboard
"""

import streamlit as st
from utils.auth import authenticate_user, get_user_by_name_and_site


# -----------------------------------------------------------
# MAIN LOGIN PAGE
# -----------------------------------------------------------

def show_login_page():
    """Display the main login page with role selection."""

    st.title("🚄 MAHSR-T3-DPR-App")
    st.subheader("Daily Progress Report System")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("Login")

        role = st.radio(
            "Select Your Role:",
            options=["Site Engineer", "Project Manager", "Admin"],
            key="login_role"
        )

        st.divider()

        if role == "Site Engineer":
            _show_engineer_login()

        elif role == "Project Manager":
            _show_pm_login()

        elif role == "Admin":
            _show_admin_login()

        st.divider()
        _show_demo_credentials()


# -----------------------------------------------------------
# SITE ENGINEER LOGIN (NAME + SITE)
# -----------------------------------------------------------

def _show_engineer_login():
    """Login for Site Engineers (name + site selection)."""

    st.write("**Site Engineer Login**")
    st.caption("Enter your name and select your site")

    name = st.text_input(
        "Full Name:",
        placeholder="e.g., Site Engineer 407",
        key="engineer_name"
    )

    site = st.selectbox(
        "Select Your Site:",
        ["TCB-407", "TCB-436", "TCB-469", "TCB-486"],
        key="engineer_site"
    )

    if st.button("Login", type="primary", use_container_width=True):

        if not name.strip():
            st.error("Please enter your name before logging in.")
            return

        user = get_user_by_name_and_site(name.strip(), site)

        if user and user.get("is_active"):
            # Force correct role
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.username = user["full_name"]
            st.session_state.user_role = "site_engineer"
            st.session_state.site_code = user["site_location"]

            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error(f"No active Site Engineer found for '{name}' at {site}.")


# -----------------------------------------------------------
# PROJECT MANAGER LOGIN
# -----------------------------------------------------------

def _show_pm_login():
    """Login for Project Managers (username + password)."""

    st.write("**Project Manager Login**")
    st.caption("Enter your credentials")

    username = st.text_input("Username:", key="pm_username")
    password = st.text_input("Password:", type="password", key="pm_password")

    if st.button("Login", type="primary", use_container_width=True):

        if not username or not password:
            st.error("Please enter both username and password.")
            return

        user = authenticate_user(username.strip(), password)

        # Ensure the user is truly PM
        if user and user.get("role") == "Administrator":
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.username = user["full_name"]
            st.session_state.user_role = "project_manager"
            st.session_state.site_code = None

            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid Project Manager credentials.")


# -----------------------------------------------------------
# ADMIN LOGIN
# -----------------------------------------------------------

def _show_admin_login():
    """Login for Admin users (username + password)."""

    st.write("**Administrator Login**")
    st.caption("Enter your credentials")

    username = st.text_input("Username:", key="admin_username")
    password = st.text_input("Password:", type="password", key="admin_password")

    if st.button("Login", type="primary", use_container_width=True):

        if not username or not password:
            st.error("Please provide both username and password.")
            return

        user = authenticate_user(username.strip(), password)

        if user and user.get("role") == "Admin":
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.username = user["full_name"]
            st.session_state.user_role = "admin"
            st.session_state.site_code = None

            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid Admin credentials.")


# -----------------------------------------------------------
# DEMO CREDENTIALS (for testing)
# -----------------------------------------------------------

def _show_demo_credentials():
    """Show sample credentials inside an expandable panel."""
    with st.expander("📋 View Demo Credentials"):
        st.markdown("""
        **Site Engineers (Name + Site only):**
        - Site Engineer 407 @ TCB-407  
        - Site Engineer 436 @ TCB-436  
        - Site Engineer 469 @ TCB-469  
        - Site Engineer 486 @ TCB-486  

        **Project Manager:**  
        - Username: `pm_user`  
        - Password: `pm123`  

        **Administrator:**  
        - Username: `admin`  
        - Password: `admin123`
        """)
