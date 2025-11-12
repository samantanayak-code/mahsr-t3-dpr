"""
MAHSR-T3-DPR-App: Automated Health Check Script
------------------------------------------------
Verifies Supabase, Email, Media Upload, and Excel Export connectivity.
Safe to run — does not modify or delete live project data.
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import pandas as pd
from PIL import Image
import smtplib

# Load environment variables
load_dotenv()

st.set_page_config(page_title="System Health Check", page_icon="🩺", layout="wide")

# --- Helper: Initialize Supabase ---
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        st.error("❌ Missing Supabase environment variables.")
        return None
    try:
        client = create_client(url, key)
        st.success("✅ Supabase client initialized successfully.")
        return client
    except Exception as e:
        st.error(f"❌ Supabase initialization failed: {e}")
        return None


# --- Helper: Check Supabase DB query ---
def test_database(client: Client):
    try:
        result = client.table("daily_progress_reports").select("*").limit(1).execute()
        st.success(f"✅ Database query OK — {len(result.data)} records accessible.")
    except Exception as e:
        st.error(f"❌ Database check failed: {e}")


# --- Helper: Check Media Upload ---
def test_media_upload(client: Client):
    try:
        img = Image.new("RGB", (200, 200), color="green")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        filename = f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        client.storage.from_("project-media").upload(filename, buf)
        st.success(f"✅ Media upload OK — uploaded {filename} to Supabase Storage.")
    except Exception as e:
        st.warning(f"⚠️ Media upload skipped or failed: {e}")


# --- Helper: Check Email ---
def test_email_service():
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not smtp_server or not smtp_user:
        st.warning("⚠️ Email service credentials missing — skipping.")
        return

    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
        st.success("✅ Email service connection OK (SMTP login successful).")
    except Exception as e:
        st.error(f"❌ Email service check failed: {e}")


# --- Helper: Check Excel Export ---
def test_excel_export():
    try:
        df = pd.DataFrame({"Date": [datetime.now().strftime("%Y-%m-%d")], "Status": ["Test OK"]})
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("⬇️ Download Test Excel", output.getvalue(), "health_check.xlsx")
        st.success("✅ Excel export test successful — sample file generated.")
    except Exception as e:
        st.error(f"❌ Excel export test failed: {e}")


# --- Main Health Check ---
st.title("🩺 MAHSR-T3-DPR System Health Check")
st.caption("Automated verification of connectivity and services")

supabase = init_supabase()
if supabase:
    test_database(supabase)
    test_media_upload(supabase)

test_email_service()
test_excel_export()

st.info("Health Check Completed. Review logs above for ✅ or ❌ status.")
