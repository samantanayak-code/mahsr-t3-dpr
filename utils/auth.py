"""
Authentication utility functions for MAHSR-T3-DPR-App
Handles user authentication and session management
"""

import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)


def authenticate_user(username: str, password: str, expected_role: str) -> dict:
    """
    Authenticate user with username and password for PM/Admin roles

    Args:
        username: User's username
        password: User's password
        expected_role: Expected role ('project_manager' or 'admin')

    Returns:
        User dict if authentication successful, None otherwise
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table("users").select("*").eq(
            "username", username
        ).eq("role", expected_role).eq("is_active", True).Single().execute()

        if response.data and response.data.get('password_hash') == password:
            update_last_login(response.data['id'])
            return response.data

        return None

    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_user_by_name_and_site(name: str, site_code: str) -> dict:
    """
    Get site engineer by name and site code (no password required)

    Args:
        name: Engineer's full name
        site_code: TCB site code (e.g., 'TCB-407')

    Returns:
        User dict if found and active, None otherwise
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table("users").select("*").eq(
            "full_name", name
        ).eq("site_location", site_code).eq(
            "role", "site_engineer"
        ).eq("is_active", True).Single().execute()

        if response.data:
            update_last_login(response.data['id'])
            return response.data

        return None

    except Exception as e:
        print(f"User lookup error: {e}")
        return None


def update_last_login(user_id: str):
    """
    Update user's last login timestamp

    Args:
        user_id: User's UUID
    """
    try:
        supabase = get_supabase_client()

        supabase.table("users").update({
            "last_login": datetime.now().isoformat()
        }).eq("id", user_id).execute()

    except Exception as e:
        print(f"Failed to update last login: {e}")


def get_user_by_id(user_id: str) -> dict:
    """
    Get user by ID

    Args:
        user_id: User's UUID

    Returns:
        User dict if found, None otherwise
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table("users").select("*").eq(
            "id", user_id
        ).maybeSingle().execute()

        return response.data

    except Exception as e:
        print(f"User lookup error: {e}")
        return None


def logout_user():
    """Clear all session state for logout"""
    import streamlit as st

    keys_to_clear = [
        'logged_in',
        'user_id',
        'username',
        'user_role',
        'site_code',
        'current_site',
        'report_date'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
