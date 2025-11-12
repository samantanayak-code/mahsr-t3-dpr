MAHSR-T3-DPR-App - Excel Export Feature
========================================

OVERVIEW
========

The Excel export feature allows Project Managers to download Daily Progress
Reports in Excel format (.xlsx) matching the layout of the reference template
"28052025-DPR.xlsx".

KEY FEATURES
============

1. Multi-site report generation
2. Date range selection (single day or multiple days)
3. Formatted Excel output with:
   - Grouped site columns
   - SCOPE/Activity rows with Target, Achieved, Cumulative
   - FTM (For The Month) calculations
   - Total summaries
   - Remarks and weather conditions section

IMPLEMENTATION FILES
====================

1. utils/export_excel.py
   - create_dpr_excel(): Generates formatted Excel file
   - get_reports_from_db(): Fetches data from Supabase
   - Uses xlsxwriter for formatting and layout

2. components/pm_dashboard.py
   - Updated "Reports" tab with working download functionality
   - Integrated export_excel utilities
   - Error handling and validation

3. EXCEL_EXPORT_TESTING.txt
   - Comprehensive testing guide
   - Step-by-step validation instructions
   - Comparison checklist with template

EXCEL FILE STRUCTURE
====================

The generated Excel file includes:

HEADER (Rows 1-4):
- Title: "MAHSR-T3 Daily Progress Report"
- Period: Date range
- Column headers:
  - S.No | SCOPE/ACTIVITY | Unit
  - For each site: Target | Achieved | Cumulative

ACTIVITY ROWS (10 activities):
1. Segment Casting (Nos)
2. Segment Demolding (Nos)
3. Segment Curing (Nos)
4. Segment Transportation (Nos)
5. Quality Inspection (Nos)
6. Reinforcement Work (Kg)
7. Concrete Work (Cu.m)
8. Formwork Installation (Sq.m)
9. Formwork Removal (Sq.m)
10. Steel Fixing (MT)

TOTAL ROW:
- Sums of all Target, Achieved, Cumulative values per site

REMARKS SECTION:
- Weather conditions
- Worker count
- General remarks per site

FORMATTING DETAILS
==================

Colors:
- Header: Blue (#4472C4) with white text
- Subheader: Light blue (#B4C7E7)
- Total row: Gray (#E7E6E6)
- Date header: Very light blue (#D9E1F2)

Alignment:
- Headers: Center
- Activity names: Left
- Numeric values: Center
- Remarks: Left

Number Format:
- All numeric values: 2 decimal places (0.00)

Borders:
- All cells have borders for print-ready format

USAGE INSTRUCTIONS
==================

FOR PROJECT MANAGERS:

1. Login to the application
2. Navigate to "Reports" tab
3. Configure report:
   - Select Report Type: "Daily Progress Report"
   - Choose From Date and To Date
   - Select one or more sites
   - Choose Export Format: "Excel (.xlsx)"
4. Click "Generate Report"
5. Wait for success message
6. Click "Download Excel Report"
7. Save file (format: DDMMYYYY-DPR.xlsx)

DATA AGGREGATION LOGIC
=======================

The export function aggregates data as follows:

TARGET:
- Sum of all target values for each activity across selected date range

ACHIEVED:
- Sum of all achieved values for each activity across selected date range

CUMULATIVE:
- Maximum cumulative value for each activity (latest/highest)
- Represents the running total up to the end date

WEATHER & REMARKS:
- Shows data from the most recent report for each site

TESTING REQUIREMENTS
====================

Before deployment, verify:

1. File Structure:
   - Headers, columns, and rows match template exactly
   - All 10 activities present and in correct order
   - Site columns grouped correctly

2. Data Accuracy:
   - Target values match database
   - Achieved values match database
   - Cumulative values match database
   - Totals calculated correctly

3. Formatting:
   - Colors match template
   - Fonts and sizes consistent
   - Borders applied correctly
   - Number formats correct (2 decimals)

4. Functionality:
   - Single site export works
   - Multi-site export works
   - Date range filtering works
   - Empty data handled gracefully
   - Error messages display correctly

KNOWN LIMITATIONS
=================

1. Excel format only (PDF and CSV coming in future phase)
2. No custom activity selection (exports all 10 activities)
3. No filtering by engineer or weather conditions
4. File generation time may increase with large date ranges

TROUBLESHOOTING
===============

Issue: "Error generating report"
Solution: Check database connection, verify Supabase credentials in .env

Issue: "Download button disabled"
Solution: Ensure at least one site is selected and dates are valid

Issue: "Empty Excel file"
Solution: Verify data exists in database for selected date range and sites

Issue: "Formatting doesn't match template"
Solution: Check xlsxwriter version, ensure it's 3.1.9+

Issue: "Numbers showing as text"
Solution: Verify number_format is applied to cells in export_excel.py

FUTURE ENHANCEMENTS
===================

Planned features:
- PDF export with same layout
- CSV export for data analysis
- Email delivery of reports
- Scheduled automatic report generation
- Custom activity selection
- Multi-period comparison reports
- Progress charts and graphs
- Export templates customization

DEPENDENCIES
============

Required packages (from requirements.txt):
- xlsxwriter==3.1.9  (Excel file generation with formatting)
- pandas==2.1.4      (Data manipulation)
- openpyxl==3.1.2    (Excel file reading, if needed)
- supabase==2.3.4    (Database connectivity)

MAINTENANCE NOTES
=================

When adding new activities:
1. Update activities_map in export_excel.py
2. Update TESTING_CHECKLIST.txt
3. Update this README
4. Test with sample data before deployment

When changing Excel format:
1. Review with stakeholders first
2. Update EXCEL_EXPORT_TESTING.txt comparison checklist
3. Preserve backward compatibility if possible
4. Document breaking changes

DATABASE SCHEMA DEPENDENCY
===========================

This feature depends on:

Tables:
- daily_reports (id, report_date, site_code, engineer_id, weather,
                total_workers, remarks, created_at, updated_at)
- report_activities (id, report_id, activity_name, unit, target,
                     achieved, cumulative, remarks)

Required relationships:
- report_activities.report_id → daily_reports.id (FK with CASCADE)

SUPPORT
=======

For issues or questions:
1. Check EXCEL_EXPORT_TESTING.txt for testing guidance
2. Review error messages in Streamlit UI
3. Check Supabase logs for database issues
4. Verify .env file has correct credentials

DEPLOYMENT CHECKLIST
====================

Before deploying to production:
[ ] All tests in EXCEL_EXPORT_TESTING.txt passed
[ ] Template comparison verified
[ ] Data accuracy validated
[ ] Error handling tested
[ ] Performance acceptable (< 10 sec for typical reports)
[ ] User documentation provided
[ ] Stakeholder approval received

VERSION HISTORY
===============

v1.0 - Initial implementation
- Basic Excel export with template matching
- Multi-site and date range support
- Formatted output with colors and borders
- Data aggregation (sum targets/achieved, max cumulative)
- Remarks and weather section
