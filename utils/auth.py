import bcrypt
from supabase import create_client
import os

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)


# =======================================================
# UNIVERSAL AUTHENTICATION (Admin + PM)
# =======================================================
def authenticate_user(username: str, password: str):
    """
    Authenticate ANY user by username + password.
    Role-based routing happens inside app.py
    """
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("username", username)
            .single()
            .execute()
        )

        if not response.data:
            return None

        user = response.data
        stored_hash = user.get("password_hash")

        if not stored_hash:
            return None

        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return user

        return None

    except Exception as e:
        print("AUTH ERROR:", e)
        return None


# =======================================================
# AUTH FOR SITE ENGINEERS (name + site)
# =======================================================
def get_user_by_name_and_site(full_name: str, site_code: str):
    """
    Authenticate Site Engineer by full name + assigned site.
    """
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("full_name", full_name)
            .eq("site_location", site_code)
            .single()
            .execute()
        )

        return response.data

    except Exception as e:
        print("ENGINEER AUTH ERROR:", e)
        return None


# =======================================================
# LOGOUT HANDLER
# =======================================================
def logout_user():
    """Clear Streamlit session state completely"""
    import streamlit as st
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.site_code = None

