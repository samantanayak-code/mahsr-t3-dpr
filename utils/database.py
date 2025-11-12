"""
Comprehensive Database CRUD Functions for MAHSR-T3-DPR-App
Handles all database operations for users, reports, and activities
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


class UserDatabase:
    """CRUD operations for users table"""

    @staticmethod
    def create_user(username: str, full_name: str, role: str,
                   site_location: Optional[str] = None,
                   password_hash: Optional[str] = None,
                   email: Optional[str] = None) -> Dict:
        """Create a new user"""
        try:
            supabase = get_supabase_client()

            user_data = {
                "username": username,
                "full_name": full_name,
                "role": role,
                "site_location": site_location,
                "password_hash": password_hash,
                "email": email,
                "is_active": True
            }

            result = supabase.table("users").insert(user_data).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("users").select("*").eq("id", user_id).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("users").select("*").eq("username", username).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def get_all_users(role: Optional[str] = None) -> List[Dict]:
        """Get all users, optionally filtered by role"""
        try:
            supabase = get_supabase_client()
            query = supabase.table("users").select("*")

            if role:
                query = query.eq("role", role)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    @staticmethod
    def get_users_by_site(site_code: str) -> List[Dict]:
        """Get all engineers for a specific site"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("users").select("*").eq(
                "site_location", site_code
            ).eq("role", "site_engineer").execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching users by site: {e}")
            return []

    @staticmethod
    def update_user(user_id: str, updates: Dict) -> Dict:
        """Update user information"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("users").update(updates).eq("id", user_id).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def deactivate_user(user_id: str) -> Dict:
        """Deactivate a user (soft delete)"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("users").update({"is_active": False}).eq("id", user_id).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ReportDatabase:
    """CRUD operations for daily_reports table"""

    @staticmethod
    def create_report(report_date: date, site_code: str, engineer_id: str,
                     weather: str, total_workers: int, remarks: str) -> Dict:
        """Create a new daily report"""
        try:
            supabase = get_supabase_client()

            report_data = {
                "report_date": report_date.isoformat(),
                "site_code": site_code,
                "engineer_id": engineer_id,
                "weather": weather,
                "total_workers": total_workers,
                "remarks": remarks
            }

            result = supabase.table("daily_reports").insert(report_data).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_report_by_id(report_id: str) -> Optional[Dict]:
        """Get report by ID"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("daily_reports").select("*").eq("id", report_id).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching report: {e}")
            return None

    @staticmethod
    def get_report_by_date_and_site(report_date: date, site_code: str) -> Optional[Dict]:
        """Get report by date and site"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("daily_reports").select("*").eq(
                "report_date", report_date.isoformat()
            ).eq("site_code", site_code).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching report: {e}")
            return None

    @staticmethod
    def get_reports_by_site(site_code: str, limit: int = 100,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[Dict]:
        """Get all reports for a site with optional date range"""
        try:
            supabase = get_supabase_client()
            query = supabase.table("daily_reports").select("*").eq("site_code", site_code)

            if start_date:
                query = query.gte("report_date", start_date.isoformat())
            if end_date:
                query = query.lte("report_date", end_date.isoformat())

            result = query.order("report_date", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []

    @staticmethod
    def get_reports_by_engineer(engineer_id: str, limit: int = 100) -> List[Dict]:
        """Get all reports by a specific engineer"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("daily_reports").select("*").eq(
                "engineer_id", engineer_id
            ).order("report_date", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []

    @staticmethod
    def get_all_reports(limit: int = 100,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> List[Dict]:
        """Get all reports across all sites"""
        try:
            supabase = get_supabase_client()
            query = supabase.table("daily_reports").select("*")

            if start_date:
                query = query.gte("report_date", start_date.isoformat())
            if end_date:
                query = query.lte("report_date", end_date.isoformat())

            result = query.order("report_date", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []

    @staticmethod
    def update_report(report_id: str, updates: Dict) -> Dict:
        """Update report information"""
        try:
            supabase = get_supabase_client()
            updates["updated_at"] = datetime.now().isoformat()
            result = supabase.table("daily_reports").update(updates).eq("id", report_id).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_report(report_id: str) -> Dict:
        """Delete a report (cascades to activities)"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("daily_reports").delete().eq("id", report_id).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ActivityDatabase:
    """CRUD operations for report_activities table"""

    @staticmethod
    def create_activity(report_id: str, activity_name: str, unit: str,
                       target: float, achieved: float, cumulative: float,
                       remarks: str = "") -> Dict:
        """Create a new activity entry"""
        try:
            supabase = get_supabase_client()

            activity_data = {
                "report_id": report_id,
                "activity_name": activity_name,
                "unit": unit,
                "target": target,
                "achieved": achieved,
                "cumulative": cumulative,
                "remarks": remarks
            }

            result = supabase.table("report_activities").insert(activity_data).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_activities_bulk(activities: List[Dict]) -> Dict:
        """Create multiple activities at once"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").insert(activities).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_activities_by_report(report_id: str) -> List[Dict]:
        """Get all activities for a report"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").select("*").eq("report_id", report_id).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []

    @staticmethod
    def get_activity_by_id(activity_id: str) -> Optional[Dict]:
        """Get activity by ID"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").select("*").eq("id", activity_id).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching activity: {e}")
            return None

    @staticmethod
    def update_activity(activity_id: str, updates: Dict) -> Dict:
        """Update activity information"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").update(updates).eq("id", activity_id).execute()
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_activity(activity_id: str) -> Dict:
        """Delete an activity"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").delete().eq("id", activity_id).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_activities_by_report(report_id: str) -> Dict:
        """Delete all activities for a report"""
        try:
            supabase = get_supabase_client()
            result = supabase.table("report_activities").delete().eq("report_id", report_id).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ReportQueries:
    """Complex queries combining reports and activities"""

    @staticmethod
    def get_complete_report(report_id: str) -> Optional[Dict]:
        """Get report with all activities"""
        report = ReportDatabase.get_report_by_id(report_id)
        if not report:
            return None

        activities = ActivityDatabase.get_activities_by_report(report_id)

        return {
            "report": report,
            "activities": activities
        }

    @staticmethod
    def get_site_summary(site_code: str, start_date: date, end_date: date) -> Dict:
        """Get summary statistics for a site in a date range"""
        reports = ReportDatabase.get_reports_by_site(
            site_code,
            limit=1000,
            start_date=start_date,
            end_date=end_date
        )

        total_reports = len(reports)
        total_workers = sum(r.get('total_workers', 0) for r in reports)

        return {
            "site_code": site_code,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_reports": total_reports,
            "total_workers": total_workers,
            "average_workers": total_workers / total_reports if total_reports > 0 else 0
        }
