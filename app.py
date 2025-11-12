"""
MAHSR-T3-DPR-App: Daily Progress Report Generator
For India's MAHSR (Mumbai-Ahmedabad High Speed Rail) Project
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

load_dotenv()

st.set_option("client.displayEnabled", True)
st.set_option('browser.gatherUsageStats', False)
st.set_page_config(
    page_title="MAHSR-T3-DPR-App",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client for data persistence"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)

supabase = init_supabase()

TCB_SITES = {
    "TCB-407": "Turbhe Casting Basin - 407",
    "TCB-436": "Turbhe Casting Basin - 436",
    "TCB-469": "Turbhe Casting Basin - 469",
    "TCB-486": "Turbhe Casting Basin - 486"
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'username' not in st.session_state:
    st.session_state.username = None

if 'site_code' not in st.session_state:
    st.session_state.site_code = None

def show_authenticated_app():
    """Display appropriate dashboard based on user role with logout in sidebar"""

    with st.sidebar:
        st.header("User Info")
        st.write(f"**Name:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role.replace('_', ' ').title()}")

        if st.session_state.site_code:
            st.write(f"**Site:** {st.session_state.site_code}")

        st.divider()

        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout_user()
            st.rerun()

        st.divider()
        st.caption(f"Session started: {datetime.now().strftime('%H:%M:%S')}")

    if st.session_state.user_role == 'site_engineer':
        show_engineer_dashboard()
    elif st.session_state.user_role == 'project_manager':
        show_pm_dashboard()
    elif st.session_state.user_role == 'admin':
        show_admin_dashboard()
    else:
        st.error("Invalid user role")
        logout_user()
        st.rerun()

    st.divider()
    st.caption("MAHSR-T3-DPR-App | Mumbai-Ahmedabad High Speed Rail Project")

def main():
    """Main application entry point with authentication routing"""

    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_authenticated_app()

if __name__ == "__main__":
    main()
