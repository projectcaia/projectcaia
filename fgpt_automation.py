import os
import logging
from datetime import datetime
import schedule
import time
import requests
import yfinance as yf
# Placeholder imports for Notion and Google APIs
from notion_client import Client as NotionClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Credentials placeholders
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
EMAIL_TO = os.getenv("EMAIL_TO")

# Initialize clients
notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None

def get_drive_service():
    if GOOGLE_CREDS_JSON and os.path.exists(GOOGLE_CREDS_JSON):
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDS_JSON,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        return build('drive', 'v3', credentials=creds)
    return None

drive_service = get_drive_service()

# Example data collection functions
def fetch_market_data():
    logging.info("Fetching market data...")
    kospi = yf.Ticker("^KS200").info
    usdkrw = yf.Ticker("KRW=X").info
    return {
        "kospi": kospi.get("regularMarketPrice"),
        "usdkrw": usdkrw.get("regularMarketPrice"),
    }

def fetch_news():
    logging.info("Fetching news...")
    # Placeholder for actual news API integration
    return ["News headline 1", "News headline 2"]

def generate_report(market_data, news_list):
    logging.info("Generating report...")
    lines = [f"Report generated at {datetime.now().isoformat()}\n"]
    lines.append(f"KOSPI200: {market_data['kospi']}")
    lines.append(f"USD/KRW: {market_data['usdkrw']}")
    lines.append("News:")
    for n in news_list:
        lines.append(f"- {n}")
    return "\n".join(lines)

def save_to_notion(content):
    if notion and NOTION_PAGE_ID:
        logging.info("Saving report to Notion...")
        notion.pages.create(parent={"page_id": NOTION_PAGE_ID}, properties={}, children=[{"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": content}}]}}])

def save_to_drive(filename, content):
    if drive_service:
        logging.info("Uploading report to Google Drive...")
        file_metadata = {"name": filename}
        media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

def send_email(content):
    if EMAIL_TO:
        logging.info("Sending report via email...")
        # Placeholder for sending email (SMTP or API)

# Routine definitions
def morning_routine():
    logging.info("Morning routine started")
    market_data = fetch_market_data()
    news = fetch_news()
    report = generate_report(market_data, news)
    save_to_notion(report)
    save_to_drive(f"morning_report_{datetime.now().date()}.txt", report)
    send_email(report)


def night_routine():
    logging.info("Night routine started")
    market_data = fetch_market_data()
    news = fetch_news()
    report = generate_report(market_data, news)
    save_to_notion(report)
    save_to_drive(f"night_report_{datetime.now().date()}.txt", report)
    send_email(report)


def schedule_jobs():
    schedule.every().day.at("09:10").do(morning_routine)
    schedule.every().day.at("23:10").do(night_routine)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    logging.info("Starting FGPT automation...")
    schedule_jobs()
