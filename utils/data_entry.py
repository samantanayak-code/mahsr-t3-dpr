"""
Data Entry Utility Functions
Handles saving, retrieving, and validating daily progress reports
"""

import os
from datetime import date, datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)


def validate_report_data(
    report_date: date,
    weather: str,
    total_workers: int,
    activities_data: List[Dict],
    general_remarks: str
) -> List[str]:
    """
    Validate daily report data before saving

    Args:
        report_date: Date of the report
        weather: Weather condition
        total_workers: Number of workers
        activities_data: List of activity dictionaries
        general_remarks: General remarks text

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not report_date:
        errors.append("Report date is required")

    if report_date > date.today():
        errors.append("Report date cannot be in the future")

    if not weather or weather.strip() == "":
        errors.append("Weather condition is required")

    if total_workers < 0:
        errors.append("Total workers cannot be negative")

    if not activities_data or len(activities_data) == 0:
        errors.append("At least one activity must be defined")

    has_any_activity = any(
        act.get('target', 0) > 0 or
        act.get('achieved', 0) > 0 or
        act.get('cumulative', 0) > 0
        for act in activities_data
    )

    if not has_any_activity:
        errors.append("At least one activity must have data entered (target, achieved, or cumulative)")

    for idx, activity in enumerate(activities_data):
        activity_name = activity.get('activity_name', f'Activity {idx+1}')

        if activity.get('achieved', 0) > activity.get('target', 0) and activity.get('target', 0) > 0:
            errors.append(f"{activity_name}: Achieved quantity cannot exceed target")

        if activity.get('target', 0) < 0:
            errors.append(f"{activity_name}: Target cannot be negative")

        if activity.get('achieved', 0) < 0:
            errors.append(f"{activity_name}: Achieved cannot be negative")

        if activity.get('cumulative', 0) < 0:
            errors.append(f"{activity_name}: Cumulative cannot be negative")

    return errors


def save_daily_report(
    report_date: date,
    site_code: str,
    engineer_id: str,
    weather: str,
    total_workers: int,
    general_remarks: str,
    activities_data: List[Dict]
) -> Dict:
    """
    Save or update daily progress report to database

    Args:
        report_date: Date of the report
        site_code: TCB site code
        engineer_id: Engineer's user ID
        weather: Weather condition
        total_workers: Number of workers
        general_remarks: General remarks
        activities_data: List of activity data

    Returns:
        Dict with success status and message/error
    """
    try:
        supabase = get_supabase_client()

        existing = supabase.table("daily_reports").select("id").eq(
            "report_date", report_date.isoformat()
        ).eq("site_code", site_code).Single().execute()

        report_data = {
            "report_date": report_date.isoformat(),
            "site_code": site_code,
            "engineer_id": engineer_id,
            "weather": weather,
            "total_workers": total_workers,
            "remarks": general_remarks,
            "updated_at": datetime.now().isoformat()
        }

        if existing.data:
            report_id = existing.data['id']

            supabase.table("daily_reports").update(report_data).eq("id", report_id).execute()

            supabase.table("report_activities").delete().eq("report_id", report_id).execute()

        else:
            report_data["created_at"] = datetime.now().isoformat()

            result = supabase.table("daily_reports").insert(report_data).execute()

            if not result.data or len(result.data) == 0:
                return {"success": False, "error": "Failed to create report"}

            report_id = result.data[0]['id']

        activities_to_insert = []
        for activity in activities_data:
            if activity['target'] > 0 or activity['achieved'] > 0 or activity['cumulative'] > 0:
                activities_to_insert.append({
                    "report_id": report_id,
                    "activity_name": activity['activity_name'],
                    "unit": activity['unit'],
                    "target": float(activity['target']),
                    "achieved": float(activity['achieved']),
                    "cumulative": float(activity['cumulative']),
                    "remarks": activity.get('remarks', '')
                })

        if activities_to_insert:
            supabase.table("report_activities").insert(activities_to_insert).execute()

        return {
            "success": True,
            "message": "Report saved successfully",
            "report_id": report_id
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_report_by_date(site_code: str, report_date: date) -> Optional[Dict]:
    """
    Retrieve a report by site and date

    Args:
        site_code: TCB site code
        report_date: Date of the report

    Returns:
        Report data dict or None if not found
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("daily_reports").select("*").eq(
            "site_code", site_code
        ).eq("report_date", report_date.isoformat()).Single().execute()

        return result.data

    except Exception as e:
        print(f"Error fetching report: {e}")
        return None


def get_reports_by_site(site_code: str, limit: int = 10) -> List[Dict]:
    """
    Get recent reports for a site

    Args:
        site_code: TCB site code
        limit: Maximum number of reports to retrieve

    Returns:
        List of report dictionaries
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("daily_reports").select("*").eq(
            "site_code", site_code
        ).order("report_date", desc=True).limit(limit).execute()

        return result.data or []

    except Exception as e:
        print(f"Error fetching reports: {e}")
        return []


def get_report_with_activities(report_id: str) -> Optional[Dict]:
    """
    Get complete report with all activities

    Args:
        report_id: Report UUID

    Returns:
        Dict with report and activities data
    """
    try:
        supabase = get_supabase_client()

        report = supabase.table("daily_reports").select("*").eq("id", report_id).Single().execute()

        if not report.data:
            return None

        activities = supabase.table("report_activities").select("*").eq(
            "report_id", report_id
        ).execute()

        return {
            "report": report.data,
            "activities": activities.data or []
        }

    except Exception as e:
        print(f"Error fetching report with activities: {e}")
        return None
