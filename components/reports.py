import streamlit as st
import pandas as pd
from datetime import datetime

def show_reports():
    """Reports and Downloads page"""
    st.title("📊 Reports & Downloads")
    
    st.write("### Available Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Daily Progress Reports")
        if st.button("📥 Download DPR Summary"):
            st.success("Report downloaded successfully!")
    
    with col2:
        st.info("Activity Reports")
        if st.button("📥 Download Activity Summary"):
            st.success("Report downloaded successfully!")
    
    st.divider()
    
    # Report filters
    st.write("### Filter Reports")
    
    date_range = st.date_input(
        "Select date range",
        value=(datetime.now(), datetime.now()),
        key="report_date_range"
    )
    
    site_filter = st.multiselect(
        "Filter by site",
        ["TCB-407", "TCB-436", "TCB-469", "TCB-486"],
        default=["TCB-407"]
    )
    
    if st.button("Generate Report"):
        st.info(f"Generating report for sites: {', '.join(site_filter)}")
