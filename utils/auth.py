from supabase import create_client
import streamlit as st

def initialize_supabase():
    """Initialize Supabase client using Streamlit secrets (for Streamlit Cloud)"""
    try:
        url = st.secrets.get("SUPABASE_URL", None)
        key = st.secrets.get("SUPABASE_KEY", None)

        if not url or not key:
            st.error("❌ Missing Supabase credentials. Please check your secrets.")
            st.info(f"URL: {'✓ Set' if url else '✗ Missing'}")
            st.info(f"KEY: {'✓ Set' if key else '✗ Missing'}")
            return None

        client = create_client(url, key)
        return client

    except Exception as e:
        st.error(f"❌ Supabase init error: {str(e)}")
        return None

def authenticate_user(username: str, password: str):
    """Authenticate user against Supabase database"""
    try:
        client = initialize_supabase()
        if not client:
            return False, "Supabase not initialized"
        
        response = client.table('users').select('*').eq('username', username).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "User not found"
        
        user = response.data[0]
        
        # Plaintext password check (replace with hashed password in production!)
        if user.get('password') != password:
            return False, "Invalid password"

        return True, user

    except Exception as e:
        return False, f"Auth error: {str(e)}"

def get_user_by_name_and_site(username: str, site_code: str):
    """Get user by username and site_code"""
    try:
        client = initialize_supabase()
        if not client:
            return None

        response = client.table('users').select('*').eq('username', username).eq('site_code', site_code).execute()
        return response.data[0] if response.data else None

    except Exception as e:
        return None

def get_supabase_client():
    """Get initialized Supabase client for other usage"""
    return initialize_supabase()
