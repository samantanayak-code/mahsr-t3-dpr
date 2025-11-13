import streamlit as st
import supabase
import os

def initialize_supabase():
    """Initialize Supabase client"""
    try:
        # Try to get from Streamlit secrets first, then from environment
        url = st.secrets.get("supabase_url") or os.getenv("SUPABASE_URL")
        key = st.secrets.get("supabase_key") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            st.error("❌ Supabase credentials not configured")
            st.info("Contact admin: SUPABASE_URL and SUPABASE_KEY environment variables need to be set")
            return None
        
        client = supabase.create_client(url, key)
        return client
    
    except Exception as e:
        st.error(f"Error initializing Supabase: {str(e)}")
        return None

def get_supabase():
    """Get or initialize Supabase client"""
    if 'supabase' not in st.session_state:
        st.session_state.supabase = initialize_supabase()
    return st.session_state.supabase
