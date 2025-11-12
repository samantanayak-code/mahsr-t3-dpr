"""
Project Manager Dashboard Component
Professional dashboard with full aggregation, charts, and color-coded status
"""

import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd
from supabase import create_client, Client
from utils.export_excel import create_dpr_excel, get_reports_from_db
from utils.analytics import (
    get_dashboard_metrics,
    get_site_wise_metrics,
    get_activity_wise_metrics,
    get_daily_trend_data,
    get_cumulative_progress,
    get_monthly_summary
)

@st.cache_resource
def get_supabase() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)


def show_overview_tab(supabase):
    """Show comprehensive overview with metrics and charts"""

    st.header("Project Overview & Analytics")

    all_sites = ["TCB-407", "TCB-436", "TCB-469", "TCB-486"]
    all_activities = [
        'Segment Casting', 'Segment Demolding', 'Segment Curing',
        'Segment Transportation', 'Quality Inspection', 'Reinforcement Work',
        'Concrete Work', 'Formwork Installation', 'Formwork Removal', 'Steel Fixing'
    ]

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        period_type = st.selectbox(
            "View Period:",
            ["Today", "Last 7 Days", "Last 30 Days", "This Month", "Custom Range"],
            key="overview_period"
        )

    with col2:
        if period_type == "Custom Range":
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                filter_start = st.date_input("From:", value=datetime.now().date() - timedelta(days=7), key="overview_start")
            with date_col2:
                filter_end = st.date_input("To:", value=datetime.now().date(), key="overview_end")
        else:
            today = datetime.now().date()
            if period_type == "Today":
                filter_start = filter_end = today
            elif period_type == "Last 7 Days":
                filter_start = today - timedelta(days=7)
                filter_end = today
            elif period_type == "Last 30 Days":
                filter_start = today - timedelta(days=30)
                filter_end = today
            else:
                filter_start = today.replace(day=1)
                filter_end = today

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    with st.spinner("Loading dashboard metrics..."):
        metrics = get_dashboard_metrics(supabase, all_sites)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Sites",
                metrics['total_sites'],
                delta=None
            )

        with col2:
            st.metric(
                "Reports Today",
                metrics['reports_today'],
                delta=None
            )

        with col3:
            progress_val = metrics['overall_progress']
            progress_color = "🟢" if progress_val >= 70 else "🟡" if progress_val >= 50 else "🔴"
            st.metric(
                "Overall Progress",
                f"{progress_val}%",
                delta=None
            )
            st.caption(f"{progress_color} Status")

        with col4:
            st.metric(
                "Total Reports",
                metrics['total_reports'],
                delta=None
            )

        st.divider()

        tab_overview, tab_sites, tab_activities = st.tabs([
            "📊 Summary Charts",
            "🏗️ Site-wise Analysis",
            "📋 Activity-wise Analysis"
        ])

        with tab_overview:
            st.subheader(f"Daily Progress Trend ({filter_start} to {filter_end})")

            dates, targets, achieved = get_daily_trend_data(supabase, all_sites, filter_start, filter_end)

            if dates and targets and achieved:
                chart_data = pd.DataFrame({
                    'Date': dates,
                    'Target': targets,
                    'Achieved': achieved
                })
                chart_data['Date'] = pd.to_datetime(chart_data['Date'])

                st.line_chart(chart_data.set_index('Date'))

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Period Target", f"{sum(targets):.2f}")
                with col2:
                    st.metric("Period Achieved", f"{sum(achieved):.2f}")
            else:
                st.info("No data available for selected period")

            st.divider()

            st.subheader("Cumulative Progress by Activity")

            cumulative_data = get_cumulative_progress(supabase, all_sites, filter_end)

            if cumulative_data:
                cum_df = pd.DataFrame(list(cumulative_data.items()), columns=['Activity', 'Cumulative'])
                cum_df = cum_df.sort_values('Cumulative', ascending=False)

                st.bar_chart(cum_df.set_index('Activity'))

                st.dataframe(
                    cum_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No cumulative data available")

        with tab_sites:
            st.subheader(f"Site-wise Metrics ({filter_start} to {filter_end})")

            site_filter = st.multiselect(
                "Filter Sites:",
                all_sites,
                default=all_sites,
                key="site_filter"
            )

            if site_filter:
                site_metrics = get_site_wise_metrics(supabase, site_filter, filter_start, filter_end)

                if site_metrics:
                    for metric in site_metrics:
                        with st.expander(f"🏗️ {metric['site_code']} - {metric['status']}", expanded=True):
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Target", f"{metric['target']:.2f}")
                            with col2:
                                st.metric("Achieved", f"{metric['achieved']:.2f}")
                            with col3:
                                st.metric("Cumulative", f"{metric['cumulative']:.2f}")
                            with col4:
                                st.metric("Progress", f"{metric['progress']:.1f}%")

                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(f"📅 Last Report: {metric['last_report']}")
                            with col2:
                                st.caption(f"📊 Reports: {metric['reports_count']}")

                            progress_bar = metric['progress'] / 100
                            st.progress(min(progress_bar, 1.0))

                    st.divider()

                    site_df = pd.DataFrame(site_metrics)
                    site_df = site_df[['site_code', 'target', 'achieved', 'cumulative', 'progress', 'reports_count']]
                    site_df.columns = ['Site', 'Target', 'Achieved', 'Cumulative', 'Progress %', 'Reports']

                    st.subheader("Site Comparison Table")
                    st.dataframe(
                        site_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.subheader("Site Performance Chart")
                    chart_df = site_df[['Site', 'Target', 'Achieved']].set_index('Site')
                    st.bar_chart(chart_df)

                else:
                    st.info("No data available for selected sites and period")
            else:
                st.warning("Please select at least one site")

        with tab_activities:
            st.subheader(f"Activity-wise Metrics ({filter_start} to {filter_end})")

            activity_filter = st.multiselect(
                "Filter Activities:",
                all_activities,
                default=all_activities,
                key="activity_filter"
            )

            if activity_filter:
                activity_metrics = get_activity_wise_metrics(
                    supabase,
                    all_sites,
                    filter_start,
                    filter_end,
                    activity_filter
                )

                if activity_metrics:
                    activity_df = pd.DataFrame(activity_metrics)

                    st.dataframe(
                        activity_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "activity": "Activity",
                            "unit": "Unit",
                            "target": st.column_config.NumberColumn("Target", format="%.2f"),
                            "achieved": st.column_config.NumberColumn("Achieved", format="%.2f"),
                            "cumulative": st.column_config.NumberColumn("Cumulative", format="%.2f"),
                            "progress": st.column_config.ProgressColumn("Progress", format="%.1f%%", min_value=0, max_value=100)
                        }
                    )

                    st.divider()

                    st.subheader("Activity Performance Chart")
                    chart_df = activity_df[['activity', 'target', 'achieved']].set_index('activity')
                    st.bar_chart(chart_df)

                    st.divider()

                    st.subheader("Cumulative Progress by Activity")
                    cum_chart_df = activity_df[['activity', 'cumulative']].set_index('activity')
                    st.bar_chart(cum_chart_df)

                else:
                    st.info("No data available for selected activities")
            else:
                st.warning("Please select at least one activity")


def show_reports_tab(supabase):
    """Show report generation and export functionality"""

    st.header("Generate & Download Reports")

    col1, col2 = st.columns(2)

    with col1:
        report_type = st.selectbox(
            "Report Type:",
            ["Daily Progress Report", "Weekly Summary", "Monthly Summary", "Custom Range"]
        )

        start_date = st.date_input("From Date:", value=datetime.now().date())
        end_date = st.date_input("To Date:", value=datetime.now().date())

    with col2:
        sites_selected = st.multiselect(
            "Select Sites:",
            ["TCB-407", "TCB-436", "TCB-469", "TCB-486"],
            default=["TCB-407", "TCB-436", "TCB-469", "TCB-486"]
        )

        format_type = st.radio(
            "Export Format:",
            ["Excel (.xlsx)", "PDF", "CSV"]
        )

    st.divider()

    if st.button("Generate Report", type="primary", use_container_width=True):
        if not sites_selected:
            st.error("Please select at least one site")
        elif start_date > end_date:
            st.error("Start date cannot be after end date")
        else:
            with st.spinner("Generating Excel report..."):
                try:
                    reports_data = get_reports_from_db(
                        supabase,
                        start_date,
                        end_date,
                        sites_selected
                    )

                    if format_type == "Excel (.xlsx)":
                        excel_file = create_dpr_excel(
                            reports_data,
                            start_date,
                            end_date,
                            sites_selected
                        )

                        filename = f"{start_date.strftime('%d%m%Y')}-DPR.xlsx"

                        st.success(f"Report generated successfully with {len(reports_data)} records")

                        st.download_button(
                            label="📥 Download Excel Report",
                            data=excel_file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.info(f"{format_type} export coming soon")

                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

    st.divider()

    st.subheader("Monthly Summary Report")

    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("Year:", min_value=2020, max_value=2030, value=datetime.now().year)
    with col2:
        month = st.number_input("Month:", min_value=1, max_value=12, value=datetime.now().month)

    if st.button("Generate Monthly Summary", use_container_width=True):
        with st.spinner("Calculating monthly summary..."):
            try:
                all_sites = ["TCB-407", "TCB-436", "TCB-469", "TCB-486"]
                monthly_data = get_monthly_summary(supabase, all_sites, year, month)

                if monthly_data:
                    st.success(f"Monthly Summary for {monthly_data['month']}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Working Days", monthly_data['working_days'])
                    with col2:
                        st.metric("Total Target", f"{monthly_data['total_target']:.2f}")
                    with col3:
                        st.metric("Total Achieved", f"{monthly_data['total_achieved']:.2f}")
                    with col4:
                        st.metric("Progress", f"{monthly_data['progress']:.1f}%")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Reports", monthly_data['total_reports'])
                    with col2:
                        st.metric("Avg Workers/Day", f"{monthly_data['avg_workers']:.0f}")

                else:
                    st.warning("No data available for selected month")

            except Exception as e:
                st.error(f"Error generating monthly summary: {str(e)}")


def show_management_tab():
    """Show management and settings"""

    st.header("Project Management")

    st.subheader("All Sites")
    sites_info = [
        {"code": "TCB-407", "name": "Turbhe Casting Basin - 407"},
        {"code": "TCB-436", "name": "Turbhe Casting Basin - 436"},
        {"code": "TCB-469", "name": "Turbhe Casting Basin - 469"},
        {"code": "TCB-486", "name": "Turbhe Casting Basin - 486"}
    ]

    for site in sites_info:
        st.write(f"**{site['code']}:** {site['name']}")

    st.divider()

    st.subheader("Dashboard Instructions")

    with st.expander("📊 Overview Tab", expanded=True):
        st.markdown("""
        **Purpose:** Real-time monitoring of all sites and activities

        **Features:**
        - Select time period (Today, Last 7 Days, Last 30 Days, This Month, Custom)
        - View overall progress with color-coded status:
          - 🟢 Green: ≥70% (Excellent)
          - 🟡 Yellow: 50-69% (On Track)
          - 🔴 Red: <50% (Needs Attention)
        - Daily trend charts showing target vs achieved
        - Cumulative progress visualization
        - Site-wise detailed metrics with status
        - Activity-wise performance analysis

        **How to Use:**
        1. Select your desired time period
        2. Use filters to focus on specific sites or activities
        3. Click Refresh to update data
        4. Review charts and metrics for insights
        5. Expand site sections for detailed information
        """)

    with st.expander("📋 Reports Tab"):
        st.markdown("""
        **Purpose:** Generate and download DPR reports

        **Features:**
        - Excel export matching 28052025-DPR.xlsx format
        - Multi-site selection
        - Date range filtering
        - Monthly summary reports

        **How to Use:**
        1. Select Report Type and date range
        2. Choose sites to include
        3. Select Export Format (Excel)
        4. Click "Generate Report"
        5. Download when ready
        """)

    with st.expander("⚙️ Management Tab"):
        st.markdown("""
        **Purpose:** View project configuration and instructions

        **Features:**
        - Site information
        - Dashboard usage guide
        - Best practices

        **Color-Coded Status Guide:**
        - 🟢 Excellent: Progress ≥90%
        - 🟡 On Track: Progress 70-89%
        - 🟠 Needs Attention: Progress 50-69%
        - 🔴 Critical: Progress <50%
        """)

    st.divider()

    st.subheader("Best Practices")
    st.markdown("""
    1. **Daily Monitoring:** Check Overview tab daily for real-time status
    2. **Weekly Reviews:** Generate weekly reports to track trends
    3. **Monthly Analysis:** Use monthly summaries for management reporting
    4. **Filter Usage:** Use site/activity filters to focus on specific areas
    5. **Status Alerts:** Pay immediate attention to red/orange status sites
    6. **Data Quality:** Ensure engineers submit daily reports for accurate metrics
    """)


def show_pm_dashboard():
    """Display Project Manager dashboard with full analytics"""

    st.title("🚄 MAHSR-T3-DPR-App")
    st.subheader("Project Manager Dashboard")

    pm_name = st.session_state.username

    st.info(f"👨‍💼 **Project Manager:** {pm_name}")

    st.divider()

    supabase = get_supabase()

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Reports", "⚙️ Management"])

    with tab1:
        show_overview_tab(supabase)

    with tab2:
        show_reports_tab(supabase)

    with tab3:
        show_management_tab()
