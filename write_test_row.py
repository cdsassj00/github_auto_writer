import os
import json

import feedparser
import gspread
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials

RSS_URL = "https://hnrss.org/frontpage"  # 일단 이걸로 안정 테스트


def html_to_text(html: str, limit: int = 3000) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    return text[:limit]


def extract_body(entry) -> str:
    # content 우선
    content_list = entry.get("content", [])
    if isinstance(content_list, list) and len(content_list) > 0:
        v = content_list[0].get("value", "")
        if v:
            return html_to_text(v)

    # 없으면 summary
    summary = entry.get("summary", "")
    if summary:
        return html_to_text(summary)

    return ""


def main():
    try:
        service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        sheet_id = os.environ["GOOGLE_SHEET_ID"]
    except Exception as e:
        raise RuntimeError(f"Env/JSON parse failed: {e}")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id).sheet1

    # 기존 링크(3열=C) 읽기
    existing_links = set(sheet.col_values(3))
    print(f"Existing links: {len(existing_links)}")

    feed = feedparser.parse(RSS_URL)

    # RSS 파싱 상태 출력 (문제 진단용)
    print(f"Feed title: {getattr(feed.feed, 'title', '')}")
    print(f"Bozo: {getattr(feed, 'bozo', 0)}")
    if getattr(feed, "bozo", 0):
        print(f"Bozo exception: {getattr(feed, 'bozo_exception', '')}")

    inserted = 0
    for entry in feed.entries[:10]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        published = entry.get("published", "")

        if not link or link in existing_links:
            continue

        body = extract_body(entry)

        row = [published, title, link, body, "rss", "source"]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        existing_links.add(link)
        inserted += 1

    print(f"Inserted {inserted} new rows")


if __name__ == "__main__":
    main()
