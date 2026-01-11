import os
import json
from datetime import datetime

import feedparser
import gspread
from google.oauth2.service_account import Credentials


RSS_URL = "https://openai.com/blog/rss.xml"  # 예시 RSS (OpenAI 블로그)


def main():
    # --- 인증 ---
    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1

    # --- RSS 읽기 ---
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[:5]:  # 최신 5개만
        published = entry.get("published", "")
        title = entry.get("title", "")
        link = entry.get("link", "")

        row = [
            published,
            title,
            link,
            "rss",
            "openai"
        ]

        sheet.append_row(row, value_input_option="USER_ENTERED")

    print(f"Inserted {len(feed.entries[:5])} rows")


if __name__ == "__main__":
    main()
