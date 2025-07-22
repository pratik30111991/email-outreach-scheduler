import os
import json
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

# Environment variables
SHEET_ID = os.getenv("SHEET_ID")
BACKEND_BASE = os.getenv("BACKEND_BASE")  # like: https://auto-email-scheduler.onrender.com
GMAIL_ID = os.getenv("GMAIL_ID")  # sender email
GMAIL_PASS = os.getenv("GMAIL_PASS")  # SMTP password
GOOGLE_JSON = os.getenv("GOOGLE_JSON")

# Setup Google Sheets API
creds_dict = json.loads(GOOGLE_JSON)
creds = service_account.Credentials.from_service_account_info(creds_dict)
service = build('sheets', 'v4', credentials=creds)

sheet_name = "Sales_Mails"
timezone = pytz.timezone("Asia/Kolkata")

def send_email(to_email, subject, message, row_num):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Unlisted Radar <{GMAIL_ID}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # Add tracking pixel
    tracking_url = f"{BACKEND_BASE}/track?id={row_num}&email={to_email}"
    pixel = f'<img src="{tracking_url}" width="1" height="1" style="display:none"/>'
    body = message + pixel

    msg.attach(MIMEText(body, "html"))

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(GMAIL_ID, GMAIL_PASS)
    server.sendmail(GMAIL_ID, to_email, msg.as_string())
    server.quit()

    return True

def run_scheduler():
    sheet_range = f"{sheet_name}!A2:K"
    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=sheet_range).execute()
    rows = result.get("values", [])

    now = datetime.now(timezone)

    for idx, row in enumerate(rows, start=2):
        try:
            name = row[1] if len(row) > 1 else ''
            email = row[2] if len(row) > 2 else ''
            subject = row[4] if len(row) > 4 else ''
            message = row[5] if len(row) > 5 else ''
            schedule_str = row[6] if len(row) > 6 else ''
            status = row[7] if len(row) > 7 else ''

            if not email or not schedule_str or status.strip().lower() == "sent":
                continue

            scheduled_time = timezone.localize(datetime.strptime(schedule_str, "%d/%m/%Y %H:%M:%S"))

            if now >= scheduled_time:
                send_email(email, subject, message, idx)
                service.spreadsheets().values().update(
                    spreadsheetId=SHEET_ID,
                    range=f"{sheet_name}!H{idx}",
                    valueInputOption="RAW",
                    body={"values": [["Sent"]]}
                ).execute()
                service.spreadsheets().values().update(
                    spreadsheetId=SHEET_ID,
                    range=f"{sheet_name}!I{idx}",
                    valueInputOption="RAW",
                    body={"values": [[now.strftime("%d/%m/%Y %H:%M:%S")]]}
                ).execute()
                print(f"Email sent to {email}")
        except Exception as e:
            print(f"Error on row {idx}: {e}")

if __name__ == "__main__":
    run_scheduler()
