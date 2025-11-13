from passlib.hash import bcrypt
from supabase import create_client
import os

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

def authenticate_user(username: str, password: str):
    """Authenticate ANY user."""
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("username", username)
            .maybe_single()
        )

        if not response or "password_hash" not in response:
            return None

        stored_hash = response["password_hash"]

        # Passlib password verification
        if stored_hash and bcrypt.verify(password, stored_hash):
            return response

        return None

    except Exception as e:
        print("AUTH ERROR:", e)
        return None


def get_user_by_name_and_site(full_name: str, site_code: str):
    """Authenticate Site Engineer (name + site)."""
    try:
        return (
            supabase.table("users")
            .select("*")
            .eq("full_name", full_name)
            .eq("site_location", site_code)
            .maybe_single()
        )
    except Exception as e:
        print("ENGINEER LOGIN ERROR:", e)
        return None


def logout_user():
    """Reset session state."""
    import streamlit as st
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.site_code = None
