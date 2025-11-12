import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

# -----------------------------------------------------------------
# Load environment and connect Supabase
# -----------------------------------------------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Supabase credentials not found. Please check environment variables.")
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------------------------------------
# Admin → Add User Page
# -----------------------------------------------------------------
def show_add_user_page():
    st.subheader("👤 Add New User (Admin Only)")
    st.caption("Create new user credentials for Site Engineers, Project Managers, or other Admins.")

    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", placeholder="e.g., site_eng_407")
            password = st.text_input("Password", type="password", placeholder="e.g., tcbl407")
        with col2:
            role = st.selectbox("Role", ["site_engineer", "project_manager", "admin"])
            site_code = st.text_input("Site Code (optional)", placeholder="e.g., TCB-407")

        submitted = st.form_submit_button("➕ Create User", use_container_width=True)

    if submitted:
        if not username or not password or not role:
            st.warning("⚠️ Please fill in all required fields.")
        else:
            try:
                # Optional: Prevent duplicates
                existing_user = supabase.table("users").select("*").eq("username", username).execute()
                if existing_user.data:
                    st.error(f"❌ User '{username}' already exists.")
                    return

                # Insert user data
                data = {
                    "username": username,
                    "password": password,   # You can hash this in future (bcrypt)
                    "role": role,
                    "site_code": site_code if site_code else None
                }
                result = supabase.table("users").insert(data).execute()

                if result.data:
                    st.success(f"✅ User '{username}' added successfully!")
                else:
                    st.error("⚠️ Something went wrong. User not added.")
            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------------------------------------------
# Optional: Allow Admin to View All Users
# -----------------------------------------------------------------
def show_existing_users():
    st.markdown("---")
    st.subheader("📋 Existing Users")

    try:
        users = supabase.table("users").select("id, username, role, site_code").execute()
        if users.data:
            st.dataframe(users.data, use_container_width=True)
        else:
            st.info("No users found in database.")
    except Exception as e:
        st.error(f"Unable to fetch users: {e}")
