import streamlit as st
import os

def initialize_supabase():
    """Initialize Supabase client from environment variables"""
    try:
        import supabase
        
        # Get credentials from environment variables (Render sets these)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError(f"Missing credentials: URL={url}, KEY={'set' if key else 'missing'}")
        
        client = supabase.create_client(url, key)
        return client
    
    except Exception as e:
        st.error(f"❌ Supabase Error: {str(e)}")
        return None

def authenticate_user(username: str, password: str):
    """Authenticate user"""
    try:
        client = initialize_supabase()
        if not client:
            return False, "Supabase not initialized"
        
        # Query users table
        response = client.table('users').select('*').eq('username', username).execute()
        
        if not response.data:
            return False, "User not found"
        
        user = response.data[0]
        
        # Check password (plaintext for demo - use bcrypt in production!)
        if user['password'] != password:
            return False, "Invalid password"
        
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

