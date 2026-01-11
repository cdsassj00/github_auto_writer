import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


def main():
    # GitHub Secrets에서 값 읽기
    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    # Google Sheets 인증
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    )
    client = gspread.authorize(creds)

    # 시트 열기 (첫 번째 시트)
    sheet = client.open_by_key(sheet_id).sheet1

    # 테스트용 한 줄 데이터
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        "GitHub Actions 테스트",
        "https://github.com",
        "이 행이 보이면 연동 성공",
        "system"
    ]

    sheet.append_row(row, value_input_option="USER_ENTERED")
    print("Row appended successfully")


if __name__ == "__main__":
    main()
