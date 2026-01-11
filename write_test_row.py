import os
import json

import feedparser
import gspread
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials


RSS_URL = "https://openai.com/blog/rss.xml"


def html_to_text(html: str) -> str:
    """RSS에 들어있는 HTML을 읽기 좋은 텍스트로 정리"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    # 너무 길면 시트가 지저분해져서 제한 (필요하면 숫자 늘리세요)
    return text[:4000]


def extract_body(entry) -> str:
    """
    RSS entry에서 본문/요약을 최대한 가져오기.
    - content:full 또는 content:encoded 가 있으면 그걸 우선
    - 없으면 summary/description 사용
    """
    # 1) content (list 형태인 경우가 많음)
    content_list = entry.get("content", [])
    if content_list and isinstance(content_list, list):
        value = content_list[0].get("value", "")
        if value:
            return html_to_text(value)

    # 2) summary (description)
    summary = entry.get("summary", "")
    if summary:
        return html_to_text(summary)

    return ""


def main():
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1

    # 기존 링크(C열) 읽어서 중복 제거
    existing_links = set(sheet.col_values(3))

    feed = feedparser.parse(RSS_URL)

    inserted = 0
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link or link in existing_links:
            continue

        published = entry.get("published", "")
        title = entry.get("title", "")
        body = extract_body(entry)

        row = [
            published,   # A: 발행일
            title,       # B: 제목
            link,        # C: 링크
            body,        # D: 내용(본문/요약 텍스트)
            "rss",       # E: 타입
            "openai"     # F: 출처
        ]

        sheet.append_row(row, value_input_option="USER_ENTERED")
        existing_links.add(link)
        inserted += 1

    print(f"Inserted {inserted} new rows")


if __name__ == "__main__":
    main()
