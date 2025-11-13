import streamlit as st
from supabase import create_client, Client
import os

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """
    Initialize and return Supabase client
    Fixed version - removes 'proxy' parameter that causes TypeError
    """
    try:
        # CORRECT: Only pass url and key parameters
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Error connecting to Supabase: {str(e)}")
        raise

def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate user against Supabase database
    """
    try:
        supabase = get_supabase_client()
        
        # Query users table
        response = supabase.table('users').select('*').eq('username', username).eq('password', password).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "user": response.data[0]}
        else:
            return {"success": False, "message": "Invalid credentials"}
            
    except Exception as e:
        return {"success": False, "message": f"Authentication error: {str(e)}"}

def get_user_by_name_and_site(username: str, site: str) -> dict:
    """
    Get user by username and site
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('users').select('*').eq('username', username).eq('site', site).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
            
    except Exception as e:
        st.error(f"Error fetching user: {str(e)}")
        return None
