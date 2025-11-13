import streamlit as st
import os

def initialize_supabase():
    """Initialize Supabase client from environment variables"""
    try:
        import supabase
        
        # Get credentials from environment - Render sets these
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            st.error(f"❌ Missing Supabase credentials")
            st.info(f"URL: {'✓ Set' if url else '✗ Missing'}")
            st.info(f"KEY: {'✓ Set' if key else '✗ Missing'}")
            return None
        
        client = supabase.create_client(url, key)
        return client
    
    except Exception as e:
        st.error(f"❌ Supabase init error: {str(e)}")
        return None

def authenticate_user(username: str, password: str):
    """Authenticate user against database"""
    try:
        client = initialize_supabase()
        if not client:
            return False, "Supabase not initialized"
        
        # Query database
        response = client.table('users').select('*').eq('username', username).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "User not found"
        
        user = response.data[0]  # Get first result
        
        # Check password
        if user.get('password') != password:
            return False, "Invalid password"
        
        # Return success with user data
        return True, user
    
    except Exception as e:
        return False, f"Auth error: {str(e)}"

def get_user_by_name_and_site(username: str, site_code: str):
    """Get user by username and site"""
    try:
        client = initialize_supabase()
        if not client:
            return None
        
        response = client.table('users').select('*').eq('username', username).eq('site_code', site_code).execute()
        return response.data[0] if response.data else None
    
    except Exception as e:
        return None

def get_supabase_client():
    """Get initialized Supabase client"""
    return initialize_supabase()


