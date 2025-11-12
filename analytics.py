"""
Analytics and Data Aggregation Utilities
For PM Dashboard metrics, charts, and reporting
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd


def get_dashboard_metrics(supabase, sites: List[str]) -> Dict:
    """
    Calculate key metrics for PM dashboard

    Args:
        supabase: Supabase client
        sites: List of site codes

    Returns:
        Dictionary with dashboard metrics
    """
    try:
        today = datetime.now().date()

        all_reports = supabase.table('daily_reports')\
            .select('*, report_activities(*)')\
            .in_('site_code', sites)\
            .execute()

        reports_today = supabase.table('daily_reports')\
            .select('id')\
            .eq('report_date', today.isoformat())\
            .in_('site_code', sites)\
            .execute()

        total_reports = len(all_reports.data) if all_reports.data else 0
        reports_today_count = len(reports_today.data) if reports_today.data else 0

        total_target = 0
        total_achieved = 0

        if all_reports.data:
            for report in all_reports.data:
                if report.get('report_activities'):
                    for activity in report['report_activities']:
                        total_target += float(activity.get('target', 0))
                        total_achieved += float(activity.get('achieved', 0))

        overall_progress = 0
        if total_target > 0:
            overall_progress = (total_achieved / total_target) * 100

        return {
            'total_sites': len(sites),
            'total_reports': total_reports,
            'reports_today': reports_today_count,
            'overall_progress': round(overall_progress, 2),
            'total_target': round(total_target, 2),
            'total_achieved': round(total_achieved, 2)
        }

    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return {
            'total_sites': len(sites),
            'total_reports': 0,
            'reports_today': 0,
            'overall_progress': 0,
            'total_target': 0,
            'total_achieved': 0
        }


def get_site_wise_metrics(supabase, sites: List[str], start_date, end_date) -> List[Dict]:
    """
    Get metrics for each site for the given period

    Args:
        supabase: Supabase client
        sites: List of site codes
        start_date: Start date
        end_date: End date

    Returns:
        List of site metric dictionaries
    """
    site_metrics = []

    try:
        for site in sites:
            response = supabase.table('daily_reports')\
                .select('*, report_activities(*)')\
                .eq('site_code', site)\
                .gte('report_date', start_date.isoformat())\
                .lte('report_date', end_date.isoformat())\
                .execute()

            reports = response.data if response.data else []

            target_sum = 0
            achieved_sum = 0
            cumulative_max = 0
            last_report_date = None

            for report in reports:
                if report.get('report_date'):
                    report_date = datetime.fromisoformat(report['report_date']).date()
                    if not last_report_date or report_date > last_report_date:
                        last_report_date = report_date

                if report.get('report_activities'):
                    for activity in report['report_activities']:
                        target_sum += float(activity.get('target', 0))
                        achieved_sum += float(activity.get('achieved', 0))
                        cumulative_val = float(activity.get('cumulative', 0))
                        if cumulative_val > cumulative_max:
                            cumulative_max = cumulative_val

            progress = 0
            if target_sum > 0:
                progress = (achieved_sum / target_sum) * 100

            status = "🔴 No Data"
            if len(reports) > 0:
                if progress >= 90:
                    status = "🟢 Excellent"
                elif progress >= 70:
                    status = "🟡 On Track"
                elif progress >= 50:
                    status = "🟠 Needs Attention"
                else:
                    status = "🔴 Critical"

            site_metrics.append({
                'site_code': site,
                'reports_count': len(reports),
                'target': round(target_sum, 2),
                'achieved': round(achieved_sum, 2),
                'cumulative': round(cumulative_max, 2),
                'progress': round(progress, 2),
                'status': status,
                'last_report': last_report_date.strftime('%d-%m-%Y') if last_report_date else 'N/A'
            })

        return site_metrics

    except Exception as e:
        print(f"Error calculating site metrics: {str(e)}")
        return []


def get_activity_wise_metrics(supabase, sites: List[str], start_date, end_date,
                               selected_activities: List[str] = None) -> List[Dict]:
    """
    Get metrics for each activity across all sites

    Args:
        supabase: Supabase client
        sites: List of site codes
        start_date: Start date
        end_date: End date
        selected_activities: List of activities to filter (None = all)

    Returns:
        List of activity metric dictionaries
    """

    activities_map = {
        'Segment Casting': 'Nos',
        'Segment Demolding': 'Nos',
        'Segment Curing': 'Nos',
        'Segment Transportation': 'Nos',
        'Quality Inspection': 'Nos',
        'Reinforcement Work': 'Kg',
        'Concrete Work': 'Cu.m',
        'Formwork Installation': 'Sq.m',
        'Formwork Removal': 'Sq.m',
        'Steel Fixing': 'MT'
    }

    if selected_activities:
        activities_map = {k: v for k, v in activities_map.items() if k in selected_activities}

    activity_metrics = []

    try:
        response = supabase.table('daily_reports')\
            .select('*, report_activities(*)')\
            .in_('site_code', sites)\
            .gte('report_date', start_date.isoformat())\
            .lte('report_date', end_date.isoformat())\
            .execute()

        reports = response.data if response.data else []

        for activity_name, unit in activities_map.items():
            target_sum = 0
            achieved_sum = 0
            cumulative_max = 0

            for report in reports:
                if report.get('report_activities'):
                    for activity in report['report_activities']:
                        if activity.get('activity_name') == activity_name:
                            target_sum += float(activity.get('target', 0))
                            achieved_sum += float(activity.get('achieved', 0))
                            cumulative_val = float(activity.get('cumulative', 0))
                            if cumulative_val > cumulative_max:
                                cumulative_max = cumulative_val

            progress = 0
            if target_sum > 0:
                progress = (achieved_sum / target_sum) * 100

            activity_metrics.append({
                'activity': activity_name,
                'unit': unit,
                'target': round(target_sum, 2),
                'achieved': round(achieved_sum, 2),
                'cumulative': round(cumulative_max, 2),
                'progress': round(progress, 2)
            })

        return activity_metrics

    except Exception as e:
        print(f"Error calculating activity metrics: {str(e)}")
        return []


def get_daily_trend_data(supabase, sites: List[str], start_date, end_date) -> Tuple[List, List, List]:
    """
    Get daily trend data for charts

    Args:
        supabase: Supabase client
        sites: List of site codes
        start_date: Start date
        end_date: End date

    Returns:
        Tuple of (dates, targets, achieved) lists
    """
    try:
        response = supabase.table('daily_reports')\
            .select('report_date, report_activities(*)')\
            .in_('site_code', sites)\
            .gte('report_date', start_date.isoformat())\
            .lte('report_date', end_date.isoformat())\
            .order('report_date')\
            .execute()

        reports = response.data if response.data else []

        daily_data = {}

        for report in reports:
            report_date = report.get('report_date')
            if not report_date:
                continue

            if report_date not in daily_data:
                daily_data[report_date] = {'target': 0, 'achieved': 0}

            if report.get('report_activities'):
                for activity in report['report_activities']:
                    daily_data[report_date]['target'] += float(activity.get('target', 0))
                    daily_data[report_date]['achieved'] += float(activity.get('achieved', 0))

        dates = sorted(daily_data.keys())
        targets = [daily_data[d]['target'] for d in dates]
        achieved = [daily_data[d]['achieved'] for d in dates]

        return dates, targets, achieved

    except Exception as e:
        print(f"Error getting trend data: {str(e)}")
        return [], [], []


def get_cumulative_progress(supabase, sites: List[str], end_date) -> Dict[str, float]:
    """
    Get cumulative progress for all activities up to end_date

    Args:
        supabase: Supabase client
        sites: List of site codes
        end_date: End date

    Returns:
        Dictionary of activity: cumulative_value
    """
    try:
        response = supabase.table('daily_reports')\
            .select('*, report_activities(*)')\
            .in_('site_code', sites)\
            .lte('report_date', end_date.isoformat())\
            .execute()

        reports = response.data if response.data else []

        cumulative_data = {}

        for report in reports:
            if report.get('report_activities'):
                for activity in report['report_activities']:
                    activity_name = activity.get('activity_name')
                    cumulative_val = float(activity.get('cumulative', 0))

                    if activity_name not in cumulative_data:
                        cumulative_data[activity_name] = 0

                    if cumulative_val > cumulative_data[activity_name]:
                        cumulative_data[activity_name] = cumulative_val

        return cumulative_data

    except Exception as e:
        print(f"Error calculating cumulative progress: {str(e)}")
        return {}


def get_monthly_summary(supabase, sites: List[str], year: int, month: int) -> Dict:
    """
    Get monthly summary for all sites

    Args:
        supabase: Supabase client
        sites: List of site codes
        year: Year
        month: Month (1-12)

    Returns:
        Dictionary with monthly summary data
    """
    try:
        from calendar import monthrange

        days_in_month = monthrange(year, month)[1]
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, days_in_month).date()

        response = supabase.table('daily_reports')\
            .select('*, report_activities(*)')\
            .in_('site_code', sites)\
            .gte('report_date', start_date.isoformat())\
            .lte('report_date', end_date.isoformat())\
            .execute()

        reports = response.data if response.data else []

        total_target = 0
        total_achieved = 0
        total_workers = 0
        working_days = set()

        for report in reports:
            working_days.add(report.get('report_date'))
            total_workers += int(report.get('total_workers', 0))

            if report.get('report_activities'):
                for activity in report['report_activities']:
                    total_target += float(activity.get('target', 0))
                    total_achieved += float(activity.get('achieved', 0))

        progress = 0
        if total_target > 0:
            progress = (total_achieved / total_target) * 100

        avg_workers = total_workers / len(working_days) if len(working_days) > 0 else 0

        return {
            'month': f"{year}-{month:02d}",
            'working_days': len(working_days),
            'total_target': round(total_target, 2),
            'total_achieved': round(total_achieved, 2),
            'progress': round(progress, 2),
            'avg_workers': round(avg_workers, 2),
            'total_reports': len(reports)
        }

    except Exception as e:
        print(f"Error calculating monthly summary: {str(e)}")
        return {}
