"""
Excel Export Utility for MAHSR-T3-DPR-App
Generates DPR reports matching the format of 28052025-DPR.xlsx
"""

import pandas as pd
import xlsxwriter
from datetime import datetime
from io import BytesIO


def create_dpr_excel(reports_data, start_date, end_date, sites):
    """
    Generate Excel file matching the DPR template format

    Args:
        reports_data: List of report dictionaries with activities
        start_date: Start date for report range
        end_date: End date for report range
        sites: List of site codes to include

    Returns:
        BytesIO object containing the Excel file
    """

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('DPR')

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    subheader_format = workbook.add_format({
        'bold': True,
        'bg_color': '#B4C7E7',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    date_header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    data_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    activity_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    number_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.00'
    })

    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 35)
    worksheet.set_column('C:C', 10)

    for col in range(3, 3 + len(sites) * 3):
        worksheet.set_column(col, col, 12)

    row = 0

    worksheet.write(row, 0, 'MAHSR-T3 Daily Progress Report', header_format)
    worksheet.merge_range(row, 0, row, 2 + len(sites) * 3,
                         'MAHSR-T3 Daily Progress Report', header_format)
    row += 1

    period_str = f"Period: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
    worksheet.write(row, 0, period_str, subheader_format)
    worksheet.merge_range(row, 0, row, 2 + len(sites) * 3, period_str, subheader_format)
    row += 1

    worksheet.merge_range(row, 0, row + 1, 0, 'S.No', header_format)
    worksheet.merge_range(row, 1, row + 1, 1, 'SCOPE / ACTIVITY', header_format)
    worksheet.merge_range(row, 2, row + 1, 2, 'Unit', header_format)

    col_offset = 3
    for site in sites:
        worksheet.merge_range(row, col_offset, row, col_offset + 2, site, header_format)
        worksheet.write(row + 1, col_offset, 'Target', subheader_format)
        worksheet.write(row + 1, col_offset + 1, 'Achieved', subheader_format)
        worksheet.write(row + 1, col_offset + 2, 'Cumulative', subheader_format)
        col_offset += 3

    row += 2

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

    reports_by_site = {}
    for report in reports_data:
        site_code = report.get('site_code')
        if site_code not in reports_by_site:
            reports_by_site[site_code] = []
        reports_by_site[site_code].append(report)

    s_no = 1
    for activity_name, unit in activities_map.items():
        worksheet.write(row, 0, s_no, data_format)
        worksheet.write(row, 1, activity_name, activity_format)
        worksheet.write(row, 2, unit, data_format)

        col_offset = 3
        for site in sites:
            site_reports = reports_by_site.get(site, [])

            target_sum = 0
            achieved_sum = 0
            cumulative_max = 0

            for report in site_reports:
                activities = report.get('activities', [])
                for activity in activities:
                    if activity.get('activity_name') == activity_name:
                        target_sum += float(activity.get('target', 0))
                        achieved_sum += float(activity.get('achieved', 0))
                        cumulative_val = float(activity.get('cumulative', 0))
                        if cumulative_val > cumulative_max:
                            cumulative_max = cumulative_val

            worksheet.write(row, col_offset, target_sum, number_format)
            worksheet.write(row, col_offset + 1, achieved_sum, number_format)
            worksheet.write(row, col_offset + 2, cumulative_max, number_format)
            col_offset += 3

        row += 1
        s_no += 1

    total_format = workbook.add_format({
        'bold': True,
        'bg_color': '#E7E6E6',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.00'
    })

    worksheet.write(row, 0, '', total_format)
    worksheet.write(row, 1, 'TOTAL', total_format)
    worksheet.write(row, 2, '', total_format)

    col_offset = 3
    for site in sites:
        site_reports = reports_by_site.get(site, [])

        total_target = 0
        total_achieved = 0
        total_cumulative = 0

        for report in site_reports:
            activities = report.get('activities', [])
            for activity in activities:
                total_target += float(activity.get('target', 0))
                total_achieved += float(activity.get('achieved', 0))
                total_cumulative += float(activity.get('cumulative', 0))

        worksheet.write(row, col_offset, total_target, total_format)
        worksheet.write(row, col_offset + 1, total_achieved, total_format)
        worksheet.write(row, col_offset + 2, total_cumulative, total_format)
        col_offset += 3

    row += 2

    remarks_header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#F2F2F2',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    worksheet.write(row, 0, 'REMARKS & WEATHER CONDITIONS', remarks_header_format)
    worksheet.merge_range(row, 0, row, 2 + len(sites) * 3,
                         'REMARKS & WEATHER CONDITIONS', remarks_header_format)
    row += 1

    for site in sites:
        site_reports = reports_by_site.get(site, [])
        if site_reports:
            latest_report = site_reports[-1]
            weather = latest_report.get('weather', 'N/A')
            workers = latest_report.get('total_workers', 0)
            remarks = latest_report.get('remarks', 'N/A')

            remark_text = f"{site}: Weather - {weather} | Workers - {workers} | {remarks}"
            worksheet.write(row, 0, remark_text, activity_format)
            worksheet.merge_range(row, 0, row, 2 + len(sites) * 3, remark_text, activity_format)
            row += 1

    workbook.close()
    output.seek(0)

    return output


def get_reports_from_db(supabase, start_date, end_date, sites):
    """
    Fetch reports from database for given date range and sites

    Args:
        supabase: Supabase client instance
        start_date: Start date
        end_date: End date
        sites: List of site codes

    Returns:
        List of report dictionaries with activities
    """

    try:
        response = supabase.table('daily_reports')\
            .select('*, report_activities(*)')\
            .gte('report_date', start_date.isoformat())\
            .lte('report_date', end_date.isoformat())\
            .in_('site_code', sites)\
            .execute()

        reports = []
        if response.data:
            for report in response.data:
                report_dict = {
                    'id': report['id'],
                    'report_date': report['report_date'],
                    'site_code': report['site_code'],
                    'weather': report.get('weather', ''),
                    'total_workers': report.get('total_workers', 0),
                    'remarks': report.get('remarks', ''),
                    'activities': []
                }

                if report.get('report_activities'):
                    for activity in report['report_activities']:
                        report_dict['activities'].append({
                            'activity_name': activity['activity_name'],
                            'unit': activity['unit'],
                            'target': activity.get('target', 0),
                            'achieved': activity.get('achieved', 0),
                            'cumulative': activity.get('cumulative', 0),
                            'remarks': activity.get('remarks', '')
                        })

                reports.append(report_dict)

        return reports

    except Exception as e:
        print(f"Error fetching reports: {str(e)}")
        return []
