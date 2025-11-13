from components.progress_dashboard import show_progress_dashboard
# ... in the role routing/menu:
if st.session_state.user_role == "project_manager":
    show_progress_dashboard()
# or call from navigation menu wherever appropriate
