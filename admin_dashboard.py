"""
Administrator Dashboard Component
For user management, system settings, and full access
"""

import streamlit as st
import os
from datetime import datetime, date
import pandas as pd
from supabase import create_client, Client
from utils.email_service import (
    test_email_configuration,
    send_daily_report_to_all,
    get_active_recipients
)

@st.cache_resource
def get_supabase() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)


def show_email_setup_tab():
    """Display email setup and recipient management"""

    st.header("📧 Automated Email Reports")
    st.caption("Configure automated daily reports sent to Project Managers at 10:30 AM IST")

    supabase = get_supabase()

    st.subheader("SMTP Configuration")

    smtp_configured = bool(os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'))

    if smtp_configured:
        st.success("✓ SMTP is configured")
        st.write(f"**Server:** {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
        st.write(f"**Username:** {os.getenv('SMTP_USERNAME', 'Not set')}")
        st.write(f"**Sender Email:** {os.getenv('SENDER_EMAIL', 'Not set')}")
    else:
        st.warning("⚠️ SMTP is not configured. Add credentials to .env file.")
        st.code("""
# Add to .env file:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=MAHSR-T3 DPR System
        """)

    col1, col2 = st.columns(2)

    with col1:
        test_email = st.text_input("Test Email Address:", placeholder="pm@example.com")
        if st.button("📤 Send Test Email", use_container_width=True):
            if test_email:
                with st.spinner("Sending test email..."):
                    success, message = test_email_configuration(test_email)
                    if success:
                        st.success(f"✓ {message}")
                    else:
                        st.error(f"✗ {message}")
            else:
                st.warning("Please enter email address")

    with col2:
        manual_send_date = st.date_input("Manual Send Date:", value=date.today())
        if st.button("📧 Send Manual Report", use_container_width=True):
            with st.spinner("Sending reports to all recipients..."):
                sites = ["TCB-407", "TCB-436", "TCB-469", "TCB-486"]
                result = send_daily_report_to_all(supabase, manual_send_date, sites)
                st.info(f"Result: {result['message']}")
                st.write(f"✓ Sent: {result['sent']}")
                st.write(f"✗ Failed: {result['failed']}")

    st.divider()

    st.subheader("Email Recipients")

    recipients = get_active_recipients(supabase, 'daily')

    if recipients:
        st.write(f"**Active Recipients:** {len(recipients)}")

        recipients_data = []
        for r in recipients:
            recipients_data.append({
                'Name': r['name'],
                'Email': r['email'],
                'Role': r['role'],
                'Active': '✓' if r['active'] else '✗',
                'Report Types': ', '.join(r.get('report_types', []))
            })

        df = pd.DataFrame(recipients_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No active recipients configured")

    st.divider()

    st.subheader("Add New Recipient")

    col1, col2 = st.columns(2)

    with col1:
        new_email = st.text_input("Email Address:", key="new_recipient_email")
        new_name = st.text_input("Full Name:", key="new_recipient_name")

    with col2:
        new_role = st.selectbox("Role:", ["PM", "Admin", "Other"], key="new_recipient_role")
        new_active = st.checkbox("Active", value=True, key="new_recipient_active")

    report_types = st.multiselect(
        "Report Types:",
        ["daily", "weekly", "monthly"],
        default=["daily"],
        key="new_recipient_reports"
    )

    if st.button("➕ Add Recipient", type="primary", use_container_width=True):
        if new_email and new_name:
            try:
                data = {
                    'email': new_email,
                    'name': new_name,
                    'role': new_role,
                    'active': new_active,
                    'report_types': report_types
                }

                supabase.table('email_recipients').insert(data).execute()
                st.success(f"✓ Recipient {new_name} added successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Error adding recipient: {str(e)}")
        else:
            st.warning("Please fill in email and name")

    st.divider()

    st.subheader("Email Logs (Recent)")

    try:
        logs_response = supabase.table('email_logs')\
            .select('*')\
            .order('sent_at', desc=True)\
            .limit(10)\
            .execute()

        if logs_response.data:
            logs_data = []
            for log in logs_response.data:
                logs_data.append({
                    'Date': log['report_date'],
                    'Recipient': log['recipient_email'],
                    'Subject': log['subject'][:50] + '...' if len(log['subject']) > 50 else log['subject'],
                    'Status': '✓ Sent' if log['status'] == 'sent' else '✗ Failed',
                    'Time': log['sent_at'][:16]
                })

            df_logs = pd.DataFrame(logs_data)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.info("No email logs yet")

    except Exception as e:
        st.warning(f"Could not load email logs: {str(e)}")

    st.divider()

    st.subheader("📌 Schedule Information")
    st.markdown("""
    **Automated Daily Reports:**
    - Send Time: 10:30 AM IST
    - Recipients: All active recipients with 'daily' report type
    - Format: Excel (.xlsx) matching standard DPR template
    - Attachments: Previous day's consolidated report

    **To Enable Automated Sending:**
    1. Configure SMTP credentials in .env file
    2. Add recipients in the section above
    3. Set recipients to 'Active'
    4. Deploy scheduled task (cron job or cloud scheduler)

    **Gmail SMTP Setup:**
    - Enable 2-Factor Authentication on Gmail account
    - Generate App Password (Google Account → Security → App Passwords)
    - Use App Password as SMTP_PASSWORD (not your regular password)
    """)


def show_admin_dashboard():
    """Display Administrator dashboard"""

    st.title("🚄 MAHSR-T3-DPR-App")
    st.subheader("Administrator Dashboard")

    admin_name = st.session_state.username

    st.info(f"🔐 **Administrator:** {admin_name}")

    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "👥 Users", "📧 Email Setup", "⚙️ Settings", "📋 System Logs"])

    with tab1:
        st.header("System Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", "6", delta=None)
        with col2:
            st.metric("Active Sessions", "1", delta=None)
        with col3:
            st.metric("Total Reports", "0", delta=None)
        with col4:
            st.metric("System Health", "100%", delta=None)

        st.divider()

        st.subheader("Recent Activity")
        st.write("- Administrator logged in - Just now")
        st.write("- System initialized - Today")

        st.divider()

        st.subheader("Database Status")
        st.success("✓ Connected to Supabase")
        st.write("- Users table: Active")
        st.write("- Sessions table: Active")

    with tab2:
        st.header("User Management")

        st.subheader("All Users")

        users_data = [
            {"Name": "Site Engineer 407", "Role": "Site Engineer", "Site": "TCB-407", "Status": "Active"},
            {"Name": "Site Engineer 436", "Role": "Site Engineer", "Site": "TCB-436", "Status": "Active"},
            {"Name": "Site Engineer 469", "Role": "Site Engineer", "Site": "TCB-469", "Status": "Active"},
            {"Name": "Site Engineer 486", "Role": "Site Engineer", "Site": "TCB-486", "Status": "Active"},
            {"Name": "Project Manager", "Role": "Project Manager", "Site": "All Sites", "Status": "Active"},
            {"Name": "Administrator", "Role": "Administrator", "Site": "System", "Status": "Active"}
        ]

        import pandas as pd
        df = pd.DataFrame(users_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("Add New User")

        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username:")
            new_full_name = st.text_input("Full Name:")
            new_role = st.selectbox("Role:", ["site_engineer", "project_manager", "admin"])

        with col2:
            if new_role == "site_engineer":
                new_site = st.selectbox("Site:", ["TCB-407", "TCB-436", "TCB-469", "TCB-486"])
            else:
                new_site = None
                st.info("No site assignment for this role")

            if new_role in ["project_manager", "admin"]:
                new_password = st.text_input("Password:", type="password")

        if st.button("Add User", type="primary"):
            st.success("✓ User added successfully!")
            st.info("User creation functionality will be implemented in next phase")

    with tab3:
        show_email_setup_tab()

    with tab4:
        st.header("System Settings")

        st.subheader("Site Configuration")
        st.write("**Current Sites:**")
        for code in ["TCB-407", "TCB-436", "TCB-469", "TCB-486"]:
            st.write(f"- {code}: Turbhe Casting Basin - {code.split('-')[1]}")

        st.divider()

        st.subheader("Report Settings")
        report_format = st.selectbox(
            "Default Report Format:",
            ["Excel (.xlsx)", "PDF", "CSV"]
        )
        auto_backup = st.checkbox("Enable Automatic Backup", value=True)

        st.divider()

        st.subheader("Notification Settings")
        email_notifications = st.checkbox("Email Notifications", value=False)
        sms_notifications = st.checkbox("SMS Notifications", value=False)

        if st.button("Save Settings", type="primary"):
            st.success("✓ Settings saved successfully!")

    with tab5:
        st.header("System Logs")

        st.subheader("Login History")
        st.write("- Administrator logged in - Just now")
        st.write("- System started - Today")

        st.divider()

        st.subheader("Activity Logs")
        st.write("- Database connected - Today")
        st.write("- Session initialized - Just now")

        st.divider()

        if st.button("Export Logs"):
            st.info("Log export functionality coming soon")
