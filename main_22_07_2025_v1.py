#!/usr/bin/env python3
# Version: 22-Jul-2025 12:15 IST v1
import os, base64, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import requests

SHEET_ID = os.getenv("SHEET_ID")
GMAIL_ID = os.getenv("GMAIL_ID")
GMAIL_PASS = os.getenv("GMAIL_PASS")
BACKEND_BASE = os.getenv("BACKEND_BASE")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_info(
    base64.b64decode(os.getenv("GOOGLE_JSON")).decode()
)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

def read_rows():
    res = sheet.values().get(spreadsheetId=SHEET_ID, range='Sheet1!A2:K').execute()
    vals = res.get('values', [])
    return [row for row in vals if row and len(row)>=8]

def write_row(idx, col, val):
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f'Sheet1!{col}{idx+2}',
        valueInputOption='RAW',
        body={'values': [[val]]}
    ).execute()

def send_email(to_email, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = GMAIL_ID
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ID, GMAIL_PASS)
        server.sendmail(GMAIL_ID, to_email, msg.as_string())

def main():
    now = datetime.now()
    rows = read_rows()
    for idx, row in enumerate(rows):
        status = row[6]
        sched = datetime.strptime(row[7], '%d/%m/%Y %H:%M:%S')
        if status.strip() != 'Ready' or now < sched:
            continue

        domain, url, title, email, draft = row[1].strip(), row[2], row[3], row[4], row[5]
        if not draft:
            resp = requests.post(
                f"{BACKEND_BASE}/draft",
                json={'domain': domain, 'page_url': url, 'title': title}
            )
            draft = resp.json().get('draft', '')
            write_row(idx, 'F', draft)

        tracking_pixel = f'<img src="{BACKEND_BASE}/track?id={idx+2}" width="1" height="1" />'
        full_body = draft + '<br><br>' + tracking_pixel

        try:
            send_email(email, f"Collaborate on content – {title}", full_body)
            write_row(idx, 'G', 'Sent')
            write_row(idx, 'H', now.strftime('%d/%m/%Y %H:%M:%S'))
        except Exception as e:
            write_row(idx, 'G', f'Error: {e}')

if __name__ == '__main__':
    main()
