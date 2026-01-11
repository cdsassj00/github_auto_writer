import os
import json
import feedparser

import gspread
from google.oauth2.service_account import Credentials


RSS_URL = "https://openai.com/blog/rss.xml"


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

    # --- 기존 링크 읽기 (중복 제거 핵심) ---
    existing_links = set(sheet.col_values(3))  # C열 (1부터 시작)
    print(f"Existing links: {len(existing_links)}")

    # --- RSS 읽기 ---
    feed = feedparser.parse(RSS_URL)

    inserted = 0

    for entry in feed.entries:
        link = entry.get("link", "")
        if not link or link in existing_links:
            continue  # 이미 있으면 건너뜀

        published = entry.get("published", "")
        title = entry.get("title", "")

        row = [
            published,
            title,
            link,
            "rss",
            "openai"
        ]

        sheet.append_row(row, value_input_option="USER_ENTERED")
        existing_links.add(link)
        inserted += 1

    print(f"Inserted {inserted} new rows")


if __name__ == "__main__":
    main()
