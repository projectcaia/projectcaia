import os
import time
from datetime import datetime, time as dtime
from notion_client import Client

# try importing optional Codex helpers for email and drive
try:
    import codex  # type: ignore
except ImportError:  # provide fallbacks if the codex package is unavailable
    class _CodexFallback:
        """Fallback methods that log output locally."""

        def send_email(self, subject: str, content: str) -> None:
            print(f"[EMAIL] {subject}\n{content}\n")

        def save_drive(self, filename: str, content: str) -> None:
            print(f"[DRIVE] {filename}\n{content}\n")

    codex = _CodexFallback()

# === [1] Alert channels configuration ===
ALARM_CHANNELS = {
    "email": True,
    "drive": True,
    "notion": True,
    "bochungki": True,  # Placeholder for Slack/webhook
}

# === [2] Notion credentials ===
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# === [3] Codex connector functions ===
def send_codex_email(subject, content):
    codex.send_email(subject=subject, content=content)


def save_to_drive(filename, content):
    codex.save_drive(filename=filename, content=content)


def send_notion_message(title, content):
    if notion and NOTION_PAGE_ID:
        notion.pages.create(
            parent={"type": "page_id", "page_id": NOTION_PAGE_ID},
            properties={"title": [{"text": {"content": title}}]},
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"type": "text", "text": {"content": content}}]
                    },
                }
            ],
        )


def send_bochungki_alarm(title, content):
    # Placeholder for Slack/Telegram/webhook notification
    print(f"[BOCHUNGKI] {title}: {content}")


# === [4] Build alarm message ===
def make_alarm_message(mode, level, data, news, strategy, sources):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = (
        f"[{now}] ({mode}) Lv{level} 감시 경보\n"
        f"지표: {data}\n\n"
        f"{news}\n\n"
        f"{strategy}\n\n"
        f"참고사이트: {', '.join(sources)}"
    )
    return msg


# === [5] Unified alert dispatch ===
def send_all_alarms(mode, level, data, news, strategy, sources):
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


# === [6] Market definitions ===
DOMESTIC_MARKETS = ["K200", "VIX_KR"]
NIGHT_MARKETS = ["SP500_F", "NASDAQ_F", "VIX", "NI225_F"]

# === [7] Alert level conditions ===
LEVEL_CONDITIONS = {
    1: {"K200": 1.2, "SP500_F": 1.0, "NASDAQ_F": 1.0, "NI225_F": 1.0, "VIX_KR": 7, "VIX": 7},
    2: {"K200": 2.0, "SP500_F": 1.8, "NASDAQ_F": 1.8, "NI225_F": 1.8, "VIX_KR": 15, "VIX": 15},
    3: {"K200": 3.0, "SP500_F": 2.5, "NASDAQ_F": 2.5, "NI225_F": 2.5, "VIX_KR": 30, "VIX": 30},
}

# === [8] Reference sites ===
DATA_SOURCES = [
    "https://finance.naver.com/",
    "https://www.investing.com/",
    "https://finance.yahoo.com/",
    "https://www.cmegroup.com/",
    "https://www.bloomberg.com/",
    "https://www.yna.co.kr/",
]

# === [9] Alarm deduplication ===
alarm_log = {"domestic": {}, "night": {}}


def is_domestic_time():
    now = datetime.now().time()
    return dtime(9, 0) <= now <= dtime(15, 30)


def is_night_time():
    now = datetime.now().time()
    return (dtime(18, 0) <= now) or (now < dtime(6, 0))


def fetch_indicators():
    # TODO: Replace with real API or crawler
    return {
        "K200": -1.5,
        "VIX_KR": 8.1,
        "SP500_F": -1.2,
        "NASDAQ_F": -1.3,
        "NI225_F": -0.9,
        "VIX": 10.5,
    }


def fetch_news_summary(mode, level, data):
    # TODO: Integrate news crawler or AI summarisation
    return f"[뉴스요약] ({mode}) Lv{level} 관련 최신 이슈: ..."


def generate_strategy_judgment(mode, level, data):
    # TODO: Implement strategy judgment or AI analysis
    return f"[전략판단] ({mode}) Lv{level}: 시장 급변에 따라 리스크 관리, 포트폴리오 조정, 관망 전략 권장."


def notify(mode, level, data):
    now = datetime.now()
    tag = now.strftime("%Y%m%d")
    if alarm_log[mode].get((level, tag)):
        return
    news = fetch_news_summary(mode, level, data)
    strategy = generate_strategy_judgment(mode, level, data)
    send_all_alarms(mode, level, data, news, strategy, DATA_SOURCES)
    alarm_log[mode][(level, tag)] = True


def check_level(data, mode):
    targets = DOMESTIC_MARKETS if mode == "domestic" else NIGHT_MARKETS
    for lvl in sorted(LEVEL_CONDITIONS):
        cond = LEVEL_CONDITIONS[lvl]
        triggered = any(
            abs(data.get(key, 0)) >= value if "VIX" not in key else data.get(key, 0) >= value
            for key, value in cond.items() if key in targets
        )
        if triggered:
            return lvl
    return None


def main_loop():
    while True:
        if is_domestic_time():
            mode = "domestic"
        elif is_night_time():
            mode = "night"
        else:
            mode = "skip"
        if mode in ["domestic", "night"]:
            data = fetch_indicators()
            level = check_level(data, mode)
            if level:
                notify(mode, level, data)
        time.sleep(60)


if __name__ == "__main__":
    main_loop()
