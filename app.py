"""
MAHSR-T3-DPR-App: Daily Progress Report System
For India's MAHSR (Mumbai–Ahmedabad High Speed Rail) Project
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

from components.login_page import show_login_page
from components.engineer_dashboard import show_engineer_dashboard
from components.pm_dashboard import show_pm_dashboard
from components.admin_dashboard import show_admin_dashboard
from utils.auth import logout_user


# ------------------------------------------------------------
# LOAD ENV
# ------------------------------------------------------------
load_dotenv()


# ------------------------------------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="MAHSR-T3-DPR-App",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ------------------------------------------------------------
# INIT SUPABASE CLIENT
# ------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)


supabase = init_supabase()


# ------------------------------------------------------------
# SESSION DEFAULTS
# ------------------------------------------------------------
defaults = {
    "logged_in": False,
    "user_role": None,
    "username": None,
    "user_id": None,
    "site_code": None
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------------------------------------------
# ROLE-BASED ROUTING (Fixed to match Supabase)
#
# Supabase roles:
#   "Admin" → show_admin_dashboard()
#   "Administrator" → show_pm_dashboard()
#   "admin" → show_engineer_dashboard()
# ------------------------------------------------------------
def show_authenticated_app():
    """Show appropriate dashboard based on authenticated user's role."""

    # ---- SIDEBAR ----
    with st.sidebar:
        st.header("User Info")
        st.write(f"**Name:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role}")

        if st.session_state.site_code:
            st.write(f"**Site:** {st.session_state.site_code}")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()

        st.caption(f"Session started at: {datetime.now().strftime('%H:%M:%S')}")

    # ---- DASHBOARD ROUTING ----
    role = st.session_state.user_role

    if role == "Admin":
        show_admin_dashboard()

    elif role == "Administrator":
        show_pm_dashboard()

    elif role == "admin":
        show_engineer_dashboard()

    else:
        st.error(f"Unknown role '{role}'. Contact Admin.")
        logout_user()
        st.rerun()

    st.divider()
    st.caption("MAHSR-T3-DPR-App | Mumbai–Ahmedabad High Speed Rail Project")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    """Primary application router."""
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_authenticated_app()


if __name__ == "__main__":
    main()
