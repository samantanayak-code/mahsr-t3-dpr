import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

st.write("Secrets keys available:", list(st.secrets.keys()))
st.write("SUPABASE_KEY value present?", bool(st.secrets.get("SUPABASE_KEY")))

# Import custom modules
from utils.auth import authenticate_user, get_user_by_name_and_site, get_supabase_client
from components.login_page import show_login_page
from components.reports import show_reports
from components.progress_dashboard import show_progress_dashboard

# Page configuration
st.set_page_config(
    page_title="MAHSR Daily Progress Tracker",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.username = None
    st.session_state.site = None
    st.session_state.user_role = None

def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    st.info("Settings page - Coming soon")
    
    with st.expander("User Information"):
        st.json(st.session_state.user)

def main():
    """Main application logic"""
    
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Show main application
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        st.sidebar.write(f"**Site:** {st.session_state.site}")
        
        # Navigation menu
        menu = st.sidebar.radio(
            "Navigation",
            ["📝 Daily Progress Entry", "📊 Reports & Downloads", "⚙️ Settings"]
        )
        
        # Logout button
        if st.sidebar.button("🚪 Logout", type="primary"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.username = None
            st.session_state.site = None
            st.session_state.user_role = None
            st.rerun()
        
        # Route to different pages based on menu selection
        if menu == "📝 Daily Progress Entry":
            show_progress_dashboard()
        elif menu == "📊 Reports & Downloads":
            show_reports()
        elif menu == "⚙️ Settings":
            show_settings()

if __name__ == "__main__":
    main()
