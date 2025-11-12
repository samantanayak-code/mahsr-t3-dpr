"""
Automated Daily Report Sender
Sends DPR reports to all active recipients at scheduled time

Usage:
  python send_daily_reports.py

For cron job (10:30 AM IST):
  30 10 * * * cd /path/to/project && python3 send_daily_reports.py >> /var/log/dpr_email.log 2>&1
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client
from utils.email_service import send_daily_report_to_all, should_send_daily_report

load_dotenv()

def main():
    """Main function to send daily reports"""

    print(f"[{date.today()}] Starting daily report email service...")

    if not should_send_daily_report():
        print("Not the scheduled time (10:30 AM IST ±5 min). Exiting.")
        return 0

    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            print("ERROR: Missing Supabase credentials in environment")
            return 1

        supabase = create_client(supabase_url, supabase_key)

        yesterday = date.today() - timedelta(days=1)
        sites = ["TCB-407", "TCB-436", "TCB-469", "TCB-486"]

        print(f"Sending reports for date: {yesterday}")
        print(f"Sites: {', '.join(sites)}")

        result = send_daily_report_to_all(supabase, yesterday, sites)

        print(f"Results:")
        print(f"  Total recipients: {result['total']}")
        print(f"  Successfully sent: {result['sent']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Message: {result['message']}")

        if result['failed'] > 0:
            print("WARNING: Some emails failed to send. Check email_logs table for details.")
            return 2

        print("Daily report email service completed successfully.")
        return 0

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
