"""
Email Service for Automated DPR Reports
Sends daily Excel reports to Project Managers via Gmail SMTP
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date
from typing import List, Dict, Tuple
import pytz


def get_ist_time() -> datetime:
    """Get current time in IST timezone"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def should_send_daily_report() -> bool:
    """
    Check if daily report should be sent (10:30 AM IST)

    Returns:
        True if current time is 10:30 AM IST (±5 minutes)
    """
    now = get_ist_time()
    target_hour = 10
    target_minute = 30

    if now.hour == target_hour and abs(now.minute - target_minute) <= 5:
        return True

    return False


def get_smtp_config() -> Dict:
    """
    Get SMTP configuration from environment variables

    Returns:
        Dictionary with SMTP settings
    """
    return {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_username': os.getenv('SMTP_USERNAME', ''),
        'smtp_password': os.getenv('SMTP_PASSWORD', ''),
        'sender_email': os.getenv('SENDER_EMAIL', ''),
        'sender_name': os.getenv('SENDER_NAME', 'MAHSR-T3 DPR System')
    }


def validate_smtp_config(config: Dict) -> Tuple[bool, str]:
    """
    Validate SMTP configuration

    Args:
        config: SMTP configuration dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['smtp_username', 'smtp_password', 'sender_email']

    for field in required_fields:
        if not config.get(field):
            return False, f"Missing required configuration: {field}"

    return True, ""


def create_email_body(report_date: date, sites: List[str], total_reports: int) -> str:
    """
    Create HTML email body

    Args:
        report_date: Date of the report
        sites: List of site codes
        total_reports: Number of reports included

    Returns:
        HTML email body
    """
    date_str = report_date.strftime('%d-%m-%Y')
    sites_list = ', '.join(sites)

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #4472C4;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .info-box {{
                background-color: white;
                border-left: 4px solid #4472C4;
                padding: 15px;
                margin: 15px 0;
            }}
            .footer {{
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #4472C4;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>�� MAHSR-T3 Daily Progress Report</h1>
            <p>Mumbai-Ahmedabad High Speed Rail Project</p>
        </div>

        <div class="content">
            <p>Dear Project Manager,</p>

            <p>Please find attached the Daily Progress Report (DPR) for <strong>{date_str}</strong>.</p>

            <div class="info-box">
                <h3>Report Summary</h3>
                <table>
                    <tr>
                        <th>Report Date</th>
                        <td>{date_str}</td>
                    </tr>
                    <tr>
                        <th>Sites Covered</th>
                        <td>{sites_list}</td>
                    </tr>
                    <tr>
                        <th>Total Reports</th>
                        <td>{total_reports}</td>
                    </tr>
                    <tr>
                        <th>Generated At</th>
                        <td>{get_ist_time().strftime('%d-%m-%Y %H:%M IST')}</td>
                    </tr>
                </table>
            </div>

            <div class="info-box">
                <h3>📎 Attachment</h3>
                <p>The attached Excel file contains detailed progress information for all activities across all sites.</p>
                <p><strong>File Format:</strong> XLSX (Excel)</p>
                <p><strong>File Structure:</strong> Matches standard DPR template format</p>
            </div>

            <p>For any queries or clarifications, please contact the project team.</p>

            <p>Best Regards,<br>
            <strong>MAHSR-T3 DPR System</strong><br>
            Automated Report Generation</p>
        </div>

        <div class="footer">
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>© 2025 MAHSR-T3 Project | Daily Progress Report System</p>
        </div>
    </body>
    </html>
    """

    return html


def send_email_with_attachment(
    recipient_email: str,
    recipient_name: str,
    subject: str,
    body_html: str,
    attachment_data: bytes,
    attachment_filename: str,
    config: Dict = None
) -> Tuple[bool, str]:
    """
    Send email with Excel attachment via Gmail SMTP

    Args:
        recipient_email: Recipient's email address
        recipient_name: Recipient's name
        subject: Email subject
        body_html: HTML email body
        attachment_data: Attachment file data (bytes)
        attachment_filename: Attachment filename
        config: SMTP configuration (optional, uses env vars if None)

    Returns:
        Tuple of (success, error_message)
    """
    if config is None:
        config = get_smtp_config()

    is_valid, error = validate_smtp_config(config)
    if not is_valid:
        return False, error

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        msg['To'] = f"{recipient_name} <{recipient_email}>"
        msg['Subject'] = subject

        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)

        attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        attachment.set_payload(attachment_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
        msg.attach(attachment)

        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.send_message(msg)

        return True, "Email sent successfully"

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check username/password."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"


def get_active_recipients(supabase, report_type: str = 'daily') -> List[Dict]:
    """
    Get active email recipients from database

    Args:
        supabase: Supabase client
        report_type: Type of report ('daily', 'weekly', etc.)

    Returns:
        List of recipient dictionaries
    """
    try:
        response = supabase.table('email_recipients')\
            .select('*')\
            .eq('active', True)\
            .execute()

        if not response.data:
            return []

        filtered_recipients = [
            recipient for recipient in response.data
            if report_type in recipient.get('report_types', [])
        ]

        return filtered_recipients

    except Exception as e:
        print(f"Error fetching recipients: {str(e)}")
        return []


def log_email_send(supabase, recipient_email: str, subject: str, report_date: date,
                   attachment_name: str, status: str, error_message: str = None) -> bool:
    """
    Log email send attempt to database

    Args:
        supabase: Supabase client
        recipient_email: Email sent to
        subject: Email subject
        report_date: Report date
        attachment_name: Attachment filename
        status: 'sent' or 'failed'
        error_message: Error details if failed

    Returns:
        True if logged successfully
    """
    try:
        data = {
            'recipient_email': recipient_email,
            'subject': subject,
            'report_date': report_date.isoformat(),
            'attachment_name': attachment_name,
            'status': status,
            'error_message': error_message
        }

        supabase.table('email_logs').insert(data).execute()
        return True

    except Exception as e:
        print(f"Error logging email: {str(e)}")
        return False


def send_daily_report_to_all(supabase, report_date: date, sites: List[str]) -> Dict:
    """
    Send daily report to all active recipients

    Args:
        supabase: Supabase client
        report_date: Date of the report
        sites: List of site codes to include

    Returns:
        Dictionary with send statistics
    """
    from utils.export_excel import create_dpr_excel, get_reports_from_db

    recipients = get_active_recipients(supabase, 'daily')

    if not recipients:
        return {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'message': 'No active recipients found'
        }

    reports_data = get_reports_from_db(supabase, report_date, report_date, sites)

    excel_file = create_dpr_excel(reports_data, report_date, report_date, sites)
    excel_data = excel_file.getvalue()

    filename = f"{report_date.strftime('%d%m%Y')}-DPR.xlsx"
    subject = f"MAHSR-T3 Daily Progress Report - {report_date.strftime('%d-%m-%Y')}"
    body_html = create_email_body(report_date, sites, len(reports_data))

    config = get_smtp_config()

    sent_count = 0
    failed_count = 0

    for recipient in recipients:
        success, error = send_email_with_attachment(
            recipient['email'],
            recipient['name'],
            subject,
            body_html,
            excel_data,
            filename,
            config
        )

        if success:
            sent_count += 1
            log_email_send(supabase, recipient['email'], subject, report_date,
                          filename, 'sent')
        else:
            failed_count += 1
            log_email_send(supabase, recipient['email'], subject, report_date,
                          filename, 'failed', error)

    return {
        'total': len(recipients),
        'sent': sent_count,
        'failed': failed_count,
        'message': f"Sent {sent_count} of {len(recipients)} emails"
    }


def test_email_configuration(test_email: str) -> Tuple[bool, str]:
    """
    Test email configuration by sending a test email

    Args:
        test_email: Email address to send test to

    Returns:
        Tuple of (success, message)
    """
    config = get_smtp_config()

    is_valid, error = validate_smtp_config(config)
    if not is_valid:
        return False, error

    subject = "MAHSR-T3 DPR System - Test Email"
    body_html = """
    <html>
    <body>
        <h2>Test Email - MAHSR-T3 DPR System</h2>
        <p>This is a test email to verify SMTP configuration.</p>
        <p>If you received this email, the configuration is working correctly.</p>
        <p>System Time: {}</p>
    </body>
    </html>
    """.format(get_ist_time().strftime('%d-%m-%Y %H:%M:%S IST'))

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        msg['To'] = test_email
        msg['Subject'] = subject

        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.send_message(msg)

        return True, "Test email sent successfully"

    except Exception as e:
        return False, f"Test email failed: {str(e)}"
