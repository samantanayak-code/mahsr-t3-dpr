"""
Site Engineer Dashboard Component
For daily data entry and site-specific progress tracking
Comprehensive DPR form matching Excel format requirements
"""

import streamlit as st
import os
from datetime import datetime, date
from supabase import create_client, Client
from utils.data_entry import save_daily_report, get_report_by_date, validate_report_data
from utils.media_upload import (
    process_and_upload_media,
    get_media_for_report,
    get_media_url,
    delete_media_file,
    is_image,
    is_video,
    format_file_size
)

@st.cache_resource
def get_supabase() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)

ACTIVITY_CONFIG = [
    {"name": "Segment Casting", "unit": "Nos"},
    {"name": "Segment Demolding", "unit": "Nos"},
    {"name": "Segment Curing", "unit": "Nos"},
    {"name": "Segment Transportation", "unit": "Nos"},
    {"name": "Quality Inspection", "unit": "Nos"},
    {"name": "Reinforcement Work", "unit": "Kg"},
    {"name": "Concrete Work", "unit": "Cu.m"},
    {"name": "Formwork Installation", "unit": "Sq.m"},
    {"name": "Formwork Removal", "unit": "Sq.m"},
    {"name": "Steel Fixing", "unit": "MT"},
]

WEATHER_OPTIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Hot", "Moderate"]

def show_engineer_dashboard():
    """Display Site Engineer dashboard"""

    st.title("🚄 MAHSR-T3-DPR-App")
    st.subheader(f"Site Engineer Dashboard - {st.session_state.site_code}")

    site_code = st.session_state.site_code
    engineer_name = st.session_state.username
    engineer_id = st.session_state.user_id

    st.info(f"👷 **Engineer:** {engineer_name} | **Site:** {site_code}")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Data Entry", "📷 Media Upload", "📊 My Reports", "👤 Profile"])

    with tab1:
        show_data_entry_form(site_code, engineer_id)

    with tab2:
        show_media_upload(site_code, engineer_id)

    with tab3:
        show_report_history(site_code, engineer_id)

    with tab4:
        show_profile(engineer_name, site_code)


def show_data_entry_form(site_code: str, engineer_id: str):
    """Display comprehensive daily progress report data entry form"""

    st.header("Daily Progress Report - Data Entry")

    report_date = st.date_input(
        "Report Date:",
        value=date.today(),
        max_value=date.today(),
        key="report_date_input",
        help="Select the date for this report"
    )

    existing_report = get_report_by_date(site_code, report_date)

    if existing_report:
        st.warning(f"⚠️ A report already exists for {report_date.strftime('%d-%m-%Y')}. You can update it below.")

    st.divider()

    st.subheader("📋 General Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Site Code:** {site_code}")
        st.write(f"**Report Date:** {report_date.strftime('%d-%m-%Y')}")

    with col2:
        weather = st.selectbox(
            "Weather Conditions:",
            options=WEATHER_OPTIONS,
            key="weather_input",
            help="Select the weather condition during work"
        )

        total_workers = st.number_input(
            "Total Workers Present:",
            min_value=0,
            max_value=500,
            value=0,
            step=1,
            key="total_workers_input",
            help="Enter total number of workers on site"
        )

    st.divider()

    st.subheader("🏗️ Activity Progress")
    st.caption("Enter progress for each activity. Leave as 0 if activity was not performed.")

    activities_data = []

    col1, col2 = st.columns(2)

    for idx, activity in enumerate(ACTIVITY_CONFIG):
        with col1 if idx % 2 == 0 else col2:
            with st.container():
                st.markdown(f"**{activity['name']}** ({activity['unit']})")

                activity_col1, activity_col2, activity_col3 = st.columns(3)

                with activity_col1:
                    target = st.number_input(
                        "Target",
                        min_value=0.0,
                        max_value=10000.0,
                        value=0.0,
                        step=0.1,
                        key=f"target_{idx}",
                        help=f"Target quantity for {activity['name']}"
                    )

                with activity_col2:
                    achieved = st.number_input(
                        "Achieved",
                        min_value=0.0,
                        max_value=10000.0,
                        value=0.0,
                        step=0.1,
                        key=f"achieved_{idx}",
                        help=f"Actual quantity achieved for {activity['name']}"
                    )

                with activity_col3:
                    cumulative = st.number_input(
                        "Cumulative",
                        min_value=0.0,
                        max_value=100000.0,
                        value=0.0,
                        step=0.1,
                        key=f"cumulative_{idx}",
                        help=f"Total cumulative progress for {activity['name']}"
                    )

                activity_remarks = st.text_input(
                    "Remarks",
                    value="",
                    key=f"activity_remarks_{idx}",
                    placeholder="Any specific notes for this activity"
                )

                activities_data.append({
                    "activity_name": activity['name'],
                    "unit": activity['unit'],
                    "target": target,
                    "achieved": achieved,
                    "cumulative": cumulative,
                    "remarks": activity_remarks
                })

                st.divider()

    st.subheader("📝 General Remarks")

    general_remarks = st.text_area(
        "Overall Remarks:",
        value="",
        height=100,
        key="general_remarks_input",
        placeholder="Enter any general observations, issues, or important notes for the day",
        help="Include delays, safety incidents, material shortages, or any other relevant information"
    )

    st.divider()

    st.subheader("📊 Summary")

    total_activities = sum(1 for act in activities_data if act['achieved'] > 0)
    total_target = sum(act['target'] for act in activities_data)
    total_achieved = sum(act['achieved'] for act in activities_data)

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("Activities with Progress", total_activities)
    with summary_col2:
        st.metric("Total Target", f"{total_target:.2f}")
    with summary_col3:
        st.metric("Total Achieved", f"{total_achieved:.2f}")

    if total_target > 0:
        progress_percentage = (total_achieved / total_target) * 100
        st.progress(min(progress_percentage / 100, 1.0))
        st.caption(f"Overall Achievement: {progress_percentage:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Report", type="primary", use_container_width=True):
            validation_errors = validate_report_data(
                report_date=report_date,
                weather=weather,
                total_workers=total_workers,
                activities_data=activities_data,
                general_remarks=general_remarks
            )

            if validation_errors:
                st.error("❌ Validation Errors:")
                for error in validation_errors:
                    st.error(f"- {error}")
            else:
                result = save_daily_report(
                    report_date=report_date,
                    site_code=site_code,
                    engineer_id=engineer_id,
                    weather=weather,
                    total_workers=total_workers,
                    general_remarks=general_remarks,
                    activities_data=activities_data
                )

                if result['success']:
                    st.success("✅ Report saved successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Error saving report: {result['error']}")

    with col2:
        if st.button("🔄 Reset Form", use_container_width=True):
            st.rerun()


def show_media_upload(site_code: str, engineer_id: str):
    """Display media upload interface for photos and videos"""

    st.header("📷 Photo & Video Upload")
    st.caption("Upload photos/videos for your daily reports. Max file size: 10MB. Images will be auto-compressed if needed.")

    supabase = get_supabase()

    select_date = st.date_input(
        "Select Report Date:",
        value=date.today(),
        max_value=date.today(),
        key="media_report_date"
    )

    existing_report = get_report_by_date(site_code, select_date)

    if not existing_report:
        st.warning(f"⚠️ No report found for {select_date.strftime('%d-%m-%Y')}. Please create a report first in the Data Entry tab.")
        return

    report_id = existing_report['id']

    st.success(f"✓ Report found for {select_date.strftime('%d-%m-%Y')}")

    st.divider()

    st.subheader("Upload New Media")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_activity = st.selectbox(
            "Select Activity:",
            options=[act['name'] for act in ACTIVITY_CONFIG],
            key="upload_activity"
        )

    with col2:
        st.caption("**File Types Allowed:**")
        st.caption("📷 Images: JPEG, PNG, WEBP")
        st.caption("🎥 Videos: MP4, MPEG, MOV, AVI")

    uploaded_file = st.file_uploader(
        "Choose photo or video file",
        type=['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mpeg', 'mov', 'avi'],
        key="media_uploader"
    )

    if uploaded_file:
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {format_file_size(uploaded_file.size)}")
            st.write(f"**Type:** {uploaded_file.type}")

        with col2:
            if is_image(uploaded_file.type):
                st.image(uploaded_file, caption="Preview", use_column_width=True)

        if st.button("📤 Upload File", type="primary", use_container_width=True):
            with st.spinner("Uploading..."):
                success, message = process_and_upload_media(
                    supabase,
                    uploaded_file,
                    report_id,
                    selected_activity,
                    site_code,
                    select_date.isoformat(),
                    engineer_id
                )

                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

    st.divider()

    st.subheader("Uploaded Media")

    media_files = get_media_for_report(supabase, report_id)

    if media_files:
        st.write(f"**Total Files:** {len(media_files)}")

        activity_groups = {}
        for media in media_files:
            activity = media['activity_name']
            if activity not in activity_groups:
                activity_groups[activity] = []
            activity_groups[activity].append(media)

        for activity_name, files in activity_groups.items():
            with st.expander(f"📁 {activity_name} ({len(files)} files)", expanded=True):
                for media in files:
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**{media['file_name']}**")
                        st.caption(f"Size: {format_file_size(media['file_size'])} | Uploaded: {media['uploaded_at'][:16]}")
                        if media['compressed']:
                            st.caption("🔄 Compressed")

                    with col2:
                        media_url = get_media_url(supabase, media['file_path'])
                        if media_url:
                            if is_image(media['file_type']):
                                if st.button("👁️ View", key=f"view_{media['id']}"):
                                    st.image(media_url, caption=media['file_name'])
                            elif is_video(media['file_type']):
                                if st.button("▶️ Play", key=f"play_{media['id']}"):
                                    st.video(media_url)

                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{media['id']}"):
                            success, error = delete_media_file(supabase, media['id'], media['file_path'])
                            if success:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error(f"Error: {error}")

                    if media_url and is_image(media['file_type']):
                        with st.container():
                            st.image(media_url, caption=media['file_name'], use_column_width=True)

                    st.divider()
    else:
        st.info("No media files uploaded for this report yet.")

    st.divider()

    st.subheader("📌 Tips")
    st.markdown("""
    - Upload photos of work progress, site conditions, and completed activities
    - Videos can document processes and safety practices
    - Images over 5MB will be automatically compressed
    - Organize media by activity for easy reference
    - Maximum 10MB per file
    """)


def show_report_history(site_code: str, engineer_id: str):
    """Display report history for the engineer"""

    st.header("My Reports")
    st.write(f"Reports for {site_code}")

    st.info("📊 Report history and detailed viewing functionality will be implemented in the next phase")

    st.subheader("Recent Reports")
    st.caption("Sample data - will be replaced with actual database queries")

    sample_data = [
        {"Date": "06-11-2025", "Activities": 5, "Workers": 25, "Status": "✅ Complete"},
        {"Date": "05-11-2025", "Activities": 6, "Workers": 28, "Status": "✅ Complete"},
        {"Date": "04-11-2025", "Activities": 4, "Workers": 22, "Status": "✅ Complete"},
    ]

    import pandas as pd
    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def show_profile(engineer_name: str, site_code: str):
    """Display engineer profile information"""

    st.header("Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        st.write(f"**Name:** {engineer_name}")
        st.write(f"**Role:** Site Engineer")
        st.write(f"**Assigned Site:** {site_code}")
        st.write(f"**Status:** 🟢 Active")

    with col2:
        st.subheader("Activity Summary")
        st.write("**Last Login:** Today")
        st.write("**Reports This Month:** 0")
        st.write("**Total Reports:** 0")

    st.divider()

    st.subheader("📊 Performance Metrics")
    st.info("Performance metrics and statistics will be implemented in the next phase")
