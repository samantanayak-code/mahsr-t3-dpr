"""
Login Page Component for MAHSR-T3-DPR-App
Handles authentication for three user roles:
- Site Engineer: Name + Site selection only
- Project Manager: Username + Password
- Admin: Username + Password
"""

import streamlit as st
from utils.auth import authenticate_user, get_user_by_name_and_site

def show_login_page():
    """Display the login page with role-based authentication"""

    st.title("🚄 MAHSR-T3-DPR-App")
    st.subheader("Daily Progress Report System")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("Login")

        role = st.radio(
            "Select Your Role:",
            options=["Site Engineer", "Project Manager", "Admin"],
            horizontal=False,
            key="login_role"
        )

        st.divider()

        if role == "Site Engineer":
            _show_engineer_login()
        elif role == "Project Manager":
            _show_pm_login()
        else:
            _show_admin_login()

        st.divider()
        _show_demo_credentials()


def _show_engineer_login():
    """Login form for Site Engineers - Name + Site only"""

    st.write("**Site Engineer Login**")
    st.caption("Enter your name and select your site")

    name = st.text_input(
        "Full Name:",
        placeholder="e.g., Site Engineer 407",
        key="engineer_name"
    )

    site = st.selectbox(
        "Select Your Site:",
        options=["TCB-407", "TCB-436", "TCB-469", "TCB-486"],
        key="engineer_site"
    )

    if st.button("Login", type="primary", use_container_width=True):
        if not name or not name.strip():
            st.error("Please enter your name")
            return

        user = get_user_by_name_and_site(name.strip(), site)

        if user and user.get('is_active'):
            st.session_state.logged_in = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['full_name']
            st.session_state.user_role = user['role']
            st.session_state.site_code = user['site_location']
            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error(f"No active account found for '{name}' at {site}")


def _show_pm_login():
    """Login form for Project Manager - Username + Password"""

    st.write("**Project Manager Login**")
    st.caption("Enter your username and password")

    username = st.text_input(
        "Username:",
        placeholder="Enter your username",
        key="pm_username"
    )

    password = st.text_input(
        "Password:",
        type="password",
        placeholder="Enter your password",
        key="pm_password"
    )

    if st.button("Login", type="primary", use_container_width=True):
        if not username or not password:
            st.error("Please enter both username and password")
            return

        user = authenticate_user(username.strip(), password, "project_manager")

        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['full_name']
            st.session_state.user_role = user['role']
            st.session_state.site_code = None
            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def _show_admin_login():
    """Login form for Admin - Username + Password"""

    st.write("**Administrator Login**")
    st.caption("Enter your admin credentials")

    username = st.text_input(
        "Username:",
        placeholder="Enter your username",
        key="admin_username"
    )

    password = st.text_input(
        "Password:",
        type="password",
        placeholder="Enter your password",
        key="admin_password"
    )

    if st.button("Login", type="primary", use_container_width=True):
        if not username or not password:
            st.error("Please enter both username and password")
            return

        user = authenticate_user(username.strip(), password, "admin")

        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['full_name']
            st.session_state.user_role = user['role']
            st.session_state.site_code = None
            st.success(f"Welcome, {user['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def _show_demo_credentials():
    """Display demo credentials for testing"""

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
