import os
from datetime import datetime
from notion_client import Client

# === [1] Alarm channel flags ===
ALARM_CHANNELS = {
    "email": True,
    "drive": True,
    "notion": True,
    "bochungki": True,
}

# === [2] Notion configuration from env ===
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# === [3] Channel helper functions ===
def send_codex_email(subject: str, content: str) -> None:
    """Placeholder for Codex email connector."""
    print(f"[EMAIL] {subject}\n{content}\n")


def save_to_drive(filename: str, content: str) -> None:
    """Placeholder for saving to Google Drive via Codex connector."""
    print(f"[DRIVE] Saving {filename}\n{content}\n")


def send_notion_message(title: str, content: str) -> None:
    if notion and NOTION_PAGE_ID:
        notion.pages.create(
            parent={"type": "page_id", "page_id": NOTION_PAGE_ID},
            properties={"title": [{"text": {"content": title}}]},
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": content}}
                        ]
                    },
                }
            ],
        )
    else:
        print(f"[NOTION] {title}\n{content}\n")


def send_bochungki_alarm(title: str, content: str) -> None:
    """Placeholder for additional alarm channel."""
    print(f"[BOCHUNGKI] {title}: {content}")

# === [4] Alarm message formatting ===
def make_alarm_message(mode: str, level: int, data: dict, news: str, strategy: str, sources: list) -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    msg = (
        f"[{now}] ({mode}) Lv{level} 감시 경보\n"
        f"지표: {data}\n\n"
        f"{news}\n\n"
        f"{strategy}\n\n"
        f"참고사이트: {', '.join(sources)}"
    )
    return msg

# === [5] Send alarms across all channels ===
def send_all_alarms(mode: str, level: int, data: dict, news: str, strategy: str, sources: list) -> None:
    msg = make_alarm_message(mode, level, data, news, strategy, sources)
    subject = f"{mode.upper()} Lv{level} 경보"
    filename = f"codex_{mode}_alarm_{datetime.now().strftime('%Y%m%d')}_Lv{level}.txt"
    if ALARM_CHANNELS.get("email"):
        send_codex_email(subject, msg)
    if ALARM_CHANNELS.get("drive"):
        save_to_drive(filename, msg)
    if ALARM_CHANNELS.get("notion"):
        send_notion_message(subject, msg)
    if ALARM_CHANNELS.get("bochungki"):
        send_bochungki_alarm(subject, msg)


# === [6] Example execution ===
if __name__ == "__main__":
    example_data = {"K200": -1.5, "SP500_F": -1.2, "VIX": 10.5}
    example_news = "[뉴스요약] 야간시장 급변 이슈 ..."
    example_strategy = "[전략판단] 위험관리, 헷지 추천 ..."
    example_sources = [
        "https://finance.naver.com/",
        "https://www.investing.com/",
        "https://finance.yahoo.com/",
        "https://www.cmegroup.com/",
        "https://www.bloomberg.com/",
        "https://www.yna.co.kr/",
    ]
    send_all_alarms("night", 2, example_data, example_news, example_strategy, example_sources)
