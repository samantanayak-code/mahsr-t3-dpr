import streamlit as st
from utils.auth import authenticate_user

def show_login_page():
    """Display login page"""
    st.title("🚄 MAHSR Daily Progress Tracker")
    st.write("### Login to Your Account")
    
    # Role selection (for UI only - actual role comes from database)
    role = st.radio("Select Your Role:", ["Site Engineer", "Project Manager", "Admin"])
    
    st.divider()
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login", use_container_width=True):
            if username and password:
                success, result = authenticate_user(username, password)
                
                if success:
                    # result is a dictionary with user data
                    st.session_state.authenticated = True
                    st.session_state.user = result
                    st.session_state.username = result['username']
                    st.session_state.site = result.get('site_code', 'N/A')
                    st.session_state.user_role = result['role']
                    st.success(f"✅ Welcome {result['username']}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.error("Please enter username and password")
    
    # Demo credentials
    with st.expander("🔓 View Demo Credentials"):
        st.markdown("""
        **Admin Account:**
        - Username: `admin`
        - Password: `admin123`
        
        **Project Manager:**
        - Username: `pm1`
        - Password: `pm123`
        
        **Site Engineer:**
        - Username: `engineer1`
        - Password: `eng123`
        """)

