"""
Database Backup and Restore Utilities for MAHSR-T3-DPR-App
Exports data to JSON format and restores from backup files
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from utils.database import (
    UserDatabase,
    ReportDatabase,
    ActivityDatabase,
    get_supabase_client
)


def backup_all_data(output_dir: str = "./data") -> Dict:
    """
    Backup all database tables to JSON files

    Args:
        output_dir: Directory to save backup files

    Returns:
        Dict with success status and file paths
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_files = {}

        users = UserDatabase.get_all_users()
        users_file = os.path.join(output_dir, f"users_backup_{timestamp}.json")
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, default=str)
        backup_files['users'] = users_file

        reports = ReportDatabase.get_all_reports(limit=10000)
        reports_file = os.path.join(output_dir, f"reports_backup_{timestamp}.json")
        with open(reports_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, default=str)
        backup_files['reports'] = reports_file

        supabase = get_supabase_client()
        activities_result = supabase.table("report_activities").select("*").limit(50000).execute()
        activities = activities_result.data or []
        activities_file = os.path.join(output_dir, f"activities_backup_{timestamp}.json")
        with open(activities_file, 'w', encoding='utf-8') as f:
            json.dump(activities, f, indent=2, default=str)
        backup_files['activities'] = activities_file

        manifest = {
            "backup_timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "tables": {
                "users": len(users),
                "reports": len(reports),
                "activities": len(activities)
            },
            "files": backup_files
        }

        manifest_file = os.path.join(output_dir, f"backup_manifest_{timestamp}.json")
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        backup_files['manifest'] = manifest_file

        return {
            "success": True,
            "message": f"Backup completed successfully at {timestamp}",
            "files": backup_files,
            "manifest": manifest
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def backup_site_data(site_code: str, output_dir: str = "./data") -> Dict:
    """
    Backup data for a specific site only

    Args:
        site_code: TCB site code
        output_dir: Directory to save backup files

    Returns:
        Dict with success status and file path
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        reports = ReportDatabase.get_reports_by_site(site_code, limit=10000)

        report_ids = [r['id'] for r in reports]
        activities = []
        for report_id in report_ids:
            activities.extend(ActivityDatabase.get_activities_by_report(report_id))

        site_data = {
            "site_code": site_code,
            "backup_timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "reports": reports,
            "activities": activities,
            "summary": {
                "total_reports": len(reports),
                "total_activities": len(activities)
            }
        }

        filename = os.path.join(output_dir, f"site_{site_code}_backup_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(site_data, f, indent=2, default=str)

        return {
            "success": True,
            "message": f"Site {site_code} backup completed successfully",
            "file": filename,
            "summary": site_data['summary']
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def restore_from_backup(backup_dir: str, manifest_file: str) -> Dict:
    """
    Restore data from backup files

    Args:
        backup_dir: Directory containing backup files
        manifest_file: Path to manifest file

    Returns:
        Dict with success status and details
    """
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        results = {
            "users": {"attempted": 0, "success": 0, "failed": 0},
            "reports": {"attempted": 0, "success": 0, "failed": 0},
            "activities": {"attempted": 0, "success": 0, "failed": 0}
        }

        if 'users' in manifest['files']:
            users_file = manifest['files']['users']
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
                results['users']['attempted'] = len(users)
                for user in users:
                    existing = UserDatabase.get_user_by_username(user['username'])
                    if not existing:
                        result = UserDatabase.create_user(
                            username=user['username'],
                            full_name=user['full_name'],
                            role=user['role'],
                            site_location=user.get('site_location'),
                            password_hash=user.get('password_hash'),
                            email=user.get('email')
                        )
                        if result['success']:
                            results['users']['success'] += 1
                        else:
                            results['users']['failed'] += 1

        if 'reports' in manifest['files']:
            reports_file = manifest['files']['reports']
            with open(reports_file, 'r', encoding='utf-8') as f:
                reports = json.load(f)
                results['reports']['attempted'] = len(reports)
                for report in reports:
                    from datetime import date
                    report_date = date.fromisoformat(report['report_date'])
                    existing = ReportDatabase.get_report_by_date_and_site(
                        report_date,
                        report['site_code']
                    )
                    if not existing:
                        result = ReportDatabase.create_report(
                            report_date=report_date,
                            site_code=report['site_code'],
                            engineer_id=report['engineer_id'],
                            weather=report['weather'],
                            total_workers=report['total_workers'],
                            remarks=report['remarks']
                        )
                        if result['success']:
                            results['reports']['success'] += 1
                        else:
                            results['reports']['failed'] += 1

        return {
            "success": True,
            "message": "Restore completed",
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def export_to_csv(site_code: str = None, output_dir: str = "./data") -> Dict:
    """
    Export reports to CSV format for Excel compatibility

    Args:
        site_code: Optional site code to filter by
        output_dir: Directory to save CSV file

    Returns:
        Dict with success status and file path
    """
    try:
        import pandas as pd
        import os

        os.makedirs(output_dir, exist_ok=True)

        if site_code:
            reports = ReportDatabase.get_reports_by_site(site_code, limit=10000)
        else:
            reports = ReportDatabase.get_all_reports(limit=10000)

        export_data = []
        for report in reports:
            activities = ActivityDatabase.get_activities_by_report(report['id'])
            for activity in activities:
                export_data.append({
                    "Report Date": report['report_date'],
                    "Site Code": report['site_code'],
                    "Engineer ID": report['engineer_id'],
                    "Weather": report['weather'],
                    "Total Workers": report['total_workers'],
                    "Activity Name": activity['activity_name'],
                    "Unit": activity['unit'],
                    "Target": activity['target'],
                    "Achieved": activity['achieved'],
                    "Cumulative": activity['cumulative'],
                    "Activity Remarks": activity['remarks'],
                    "General Remarks": report['remarks']
                })

        df = pd.DataFrame(export_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_suffix = f"_{site_code}" if site_code else "_all_sites"
        filename = os.path.join(output_dir, f"dpr_export{site_suffix}_{timestamp}.csv")

        df.to_csv(filename, index=False, encoding='utf-8')

        return {
            "success": True,
            "message": f"Exported {len(export_data)} records to CSV",
            "file": filename,
            "records": len(export_data)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_manual_backup() -> Dict:
    """
    Create a manual backup with user-friendly naming
    Convenience function for quick backups
    """
    return backup_all_data()


def list_backups(backup_dir: str = "./data") -> List[Dict]:
    """
    List all available backups in the directory

    Args:
        backup_dir: Directory containing backups

    Returns:
        List of backup information
    """
    try:
        if not os.path.exists(backup_dir):
            return []

        manifests = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("backup_manifest_") and filename.endswith(".json"):
                filepath = os.path.join(backup_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    manifests.append({
                        "manifest_file": filepath,
                        "timestamp": manifest.get("backup_timestamp"),
                        "date": manifest.get("backup_date"),
                        "tables": manifest.get("tables", {})
                    })

        manifests.sort(key=lambda x: x['timestamp'], reverse=True)
        return manifests

    except Exception as e:
        print(f"Error listing backups: {e}")
        return []
