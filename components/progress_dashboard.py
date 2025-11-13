from components.progress_dashboard import show_progress_dashboard
# ... in the role routing/menu:
if st.session_state.user_role == "project_manager":
    show_progress_dashboard()
# or call from navigation menu wherever appropriate
# components/progress_dashboard.py
import io
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

# Try to reuse your existing utils functions if present; otherwise use low-level queries.
try:
    from utils.data_entry import get_supabase_client, get_reports_by_date_range  # optional helpers
except Exception:
    # we will import a generic client getter below if helper missing
    get_reports_by_date_range = None
    try:
        from utils.data_entry import get_supabase_client
    except Exception:
        get_supabase_client = None

# Optional helper: an export helper if you already have one
try:
    from utils.export_excel import create_excel_from_reports  # optional
except Exception:
    create_excel_from_reports = None


def _query_reports(supabase, start_date: str, end_date: str, site_codes: Optional[List[str]] = None) -> List[Dict]:
    """
    Query supabase table 'daily_progress_reports' between dates.
    Returns list of dict rows.
    """
    # Supabase table name - adapt if your table name differs
    table_name = "daily_progress_reports"

    q = supabase.table(table_name).select("*").gte("entry_date", start_date).lte("entry_date", end_date)
    if site_codes:
        # filter by site_code values
        q = q.in_("site_code", site_codes)
    resp = q.execute()
    if hasattr(resp, "data"):
        return resp.data or []
    # fallback older interface
    return resp or []


def _normalize_reports(rows: List[Dict]) -> pd.DataFrame:
    """Normalise list of dicts to a pandas DataFrame with safe types."""
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # convert entry_date to datetime.date if needed
    if "entry_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    # ensure numeric columns are numeric
    for col in ["quantity", "progress_percent"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def _excel_bytes_from_df(df: pd.DataFrame, sheet_name: str = "DPR") -> bytes:
    """Return an in-memory Excel file bytes for download."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
    buf.seek(0)
    return buf.read()


def show_progress_dashboard():
    st.title("📊 Daily Progress Dashboard — MAHSR T3")

    # -----------------------------
    # 1. Build connection / get helper
    # -----------------------------
    supabase = None
    if get_supabase_client:
        try:
            supabase = get_supabase_client()
        except Exception as e:
            st.error(f"Could not initialize Supabase client from utils: {e}")
            st.stop()
    else:
        # Try to import a generic client from utils.database or utils.data_entry
        try:
            from utils.data_entry import get_supabase_client as _client_getter
            supabase = _client_getter()
        except Exception as e:
            st.error("Supabase client helper not found in utils.data_entry. Ensure get_supabase_client() exists.")
            st.stop()

    # -----------------------------
    # 2. Filters: date range & sites
    # -----------------------------
    with st.sidebar:
        st.header("Filters")
        today = date.today()
        default_from = today - timedelta(days=14)
        date_from = st.date_input("From", value=default_from)
        date_to = st.date_input("To", value=today)
        # site filter: fetch distinct site codes dynamically if possible
        all_sites = []
        try:
            _sites_q = supabase.table("daily_progress_reports").select("site_code", count="exact").limit(1000).execute()
            if hasattr(_sites_q, "data") and _sites_q.data:
                _sites = list({r.get("site_code") for r in _sites_q.data if r.get("site_code")})
                all_sites = sorted([s for s in _sites if s])
        except Exception:
            all_sites = []

        site_filter = st.multiselect("Site(s)", options=all_sites, default=all_sites if len(all_sites) <= 3 else [])
        st.markdown("---")
        st.markdown("**Quick ranges**")
        if st.button("Last 7 days"):
            date_from = today - timedelta(days=7)
            date_to = today
        if st.button("Last 30 days"):
            date_from = today - timedelta(days=30)
            date_to = today

    # -----------------------------
    # 3. Fetch reports
    # -----------------------------
    start_date_str = date_from.isoformat()
    end_date_str = date_to.isoformat()

    with st.spinner("Fetching reports from database..."):
        try:
            if get_reports_by_date_range:
                rows = get_reports_by_date_range(start_date_str, end_date_str, site_codes=site_filter)
            else:
                rows = _query_reports(supabase, start_date_str, end_date_str, site_codes=site_filter)
        except Exception as e:
            st.error(f"Failed to fetch reports: {e}")
            st.stop()

    df = _normalize_reports(rows)

    # -----------------------------
    # 4. KPIs and site summary
    # -----------------------------
    col1, col2, col3 = st.columns(3)
    total_entries = len(df)
    total_qty = df["quantity"].sum() if "quantity" in df.columns else 0
    avg_progress = df["progress_percent"].mean() if "progress_percent" in df.columns and not df["progress_percent"].empty else 0

    col1.metric("Total Records", total_entries)
    col2.metric("Total Quantity", f"{total_qty:.2f}")
    col3.metric("Avg Progress (%)", f"{avg_progress:.1f}")

    st.markdown("### Site-wise Summary")
    if df.empty:
        st.info("No records for the selected range/filters.")
    else:
        # Group by site
        if "site_code" in df.columns:
            site_grp = df.groupby("site_code").agg(
                records=("entry_date", "count"),
                total_qty=("quantity", "sum"),
                avg_progress=("progress_percent", "mean")
            ).reset_index().sort_values("records", ascending=False)
            st.dataframe(site_grp, use_container_width=True)
        else:
            st.write("No site_code found in dataset.")

    # -----------------------------
    # 5. Date-wise table & filters
    # -----------------------------
    st.markdown("### Date-wise Details")
    if not df.empty:
        # Show table
        st.dataframe(df.sort_values(["entry_date", "site_code"], ascending=[False, True]), use_container_width=True)

        # Filtering controls for chart
        chart_site = st.selectbox("Select site for charts (or All)", options=["All"] + (sorted(df["site_code"].unique().tolist()) if "site_code" in df.columns else []))
        chart_df = df.copy()
        if chart_site and chart_site != "All" and "site_code" in chart_df.columns:
            chart_df = chart_df[chart_df["site_code"] == chart_site]

        # -----------------------------
        # 6. Charts - Progress over time and quantity
        # -----------------------------
        st.markdown("### Charts")
        if not chart_df.empty:
            # Daily progress trend
            if "entry_date" in chart_df.columns and "progress_percent" in chart_df.columns:
                trend = chart_df.groupby("entry_date").agg(avg_progress=("progress_percent", "mean")).reset_index()
                fig1 = px.line(trend, x="entry_date", y="avg_progress", title="Avg Progress over Time")
                st.plotly_chart(fig1, use_container_width=True)

            # Quantity by work_item
            if "work_item" in chart_df.columns and "quantity" in chart_df.columns:
                qby = chart_df.groupby("work_item").agg(total_qty=("quantity", "sum")).reset_index().sort_values("total_qty", ascending=False).head(20)
                fig2 = px.bar(qby, x="work_item", y="total_qty", title="Top work items by Quantity")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No chartable data for the selected site/date range.")

        # -----------------------------
        # 7. Export to Excel
        # -----------------------------
        st.markdown("### Export")
        if create_excel_from_reports:
            # use your helper if present
            try:
                excel_bytes = create_excel_from_reports(df)
            except Exception:
                excel_bytes = _excel_bytes_from_df(df)
        else:
            excel_bytes = _excel_bytes_from_df(df)

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
        filename = f"mahsr_dpr_{start_date_str}_to_{end_date_str}_{ts}.xlsx"
        st.download_button("Download Excel", data=excel_bytes, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No records to display or export for the selected filters.")
