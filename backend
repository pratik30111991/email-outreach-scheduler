# Version: 22-Jul-2025 12:20 IST v1
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import io, os, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'

@app.route('/draft', methods=['POST'])
def draft():
    data = request.get_json()
    draft = (
        f"Hi there,\n\n"
        f"I found your page titled \"{data['title']}\" at {data['page_url']}.\n"
        f"I run YoTIX and think a brief mention could benefit your readers.\n\n"
        "Would you like me to contribute a short case study or quote?\n\nCheers,\nGaurav"
    )
    return jsonify({'draft': draft})

@app.route('/track')
def track():
    row = request.args.get('id')
    SHEET_ID = os.getenv("SHEET_ID")
    creds = service_account.Credentials.from_service_account_info(
        base64.b64decode(os.getenv("GOOGLE_JSON")).decode()
    )
    svc = build('sheets', 'v4', credentials=creds)
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f'Sheet1!J{row}',
        valueInputOption='RAW',
        body={'values': [['Yes']]}
    ).execute()
    svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f'Sheet1!K{row}',
        valueInputOption='RAW',
        body={'values': [[ts]]}
    ).execute()
    return send_file(io.BytesIO(pixel), mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
