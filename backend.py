from flask import Flask, request, send_file
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os
import io
import json

app = Flask(__name__)

GIF_BYTES = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF!\xF9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

@app.route('/track')
def track():
    row = request.args.get("id")
    email_param = request.args.get("email")

    if not row or not email_param:
        return send_file(io.BytesIO(GIF_BYTES), mimetype='image/gif')

    SHEET_ID = os.getenv("SHEET_ID")
    GOOGLE_JSON = os.getenv("GOOGLE_JSON")
    creds_dict = json.loads(GOOGLE_JSON)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    service = build('sheets', 'v4', credentials=creds)

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sheet_name = "Sales_Mails"

    try:
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!J{row}",
            valueInputOption="RAW",
            body={"values": [["Yes"]]}
        ).execute()

        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!K{row}",
            valueInputOption="RAW",
            body={"values": [[now]]}
        ).execute()

        print(f"Opened by {email_param} - Row {row}")
    except Exception as e:
        print(f"Error updating tracking: {e}")

    return send_file(io.BytesIO(GIF_BYTES), mimetype="image/gif")
