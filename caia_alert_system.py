# Market monitoring and strategy alerts for Caia (센티넬/전략판단 알림)

import logging
import time
from datetime import datetime
import yfinance as yf
from bs4 import BeautifulSoup
import requests

# 커넥터 연동 함수 (ChatGPT Codex 기준)
def send_codex_email(subject, content):
    codex.send_email(subject=subject, content=content)

def save_to_drive(filename, content):
    codex.save_drive(filename=filename, content=content)

# 데이터/지표 사이트
DATA_SITES = [
    "https://finance.naver.com/",
    "https://www.investing.com/",
    "https://finance.yahoo.com/",
    "https://www.cmegroup.com/",
    "https://www.bloomberg.com/",
    "https://www.yna.co.kr/"
]

# 심볼/임계치 예시 (필요시 확장)
SYMBOLS = {
    "K200": "KS200",
    "SP500_F": "ES=F",
    "NASDAQ_F": "NQ=F",
    "VIX": "VIX",
}

LEVEL_THRESHOLDS = {
    1: {"K200": 1.2, "SP500_F": 1.0, "NASDAQ_F": 1.0, "VIX": 7.0},
    2: {"K200": 2.0, "SP500_F": 1.8, "NASDAQ_F": 1.8, "VIX": 15.0},
    3: {"K200": 3.0, "SP500_F": 2.5, "NASDAQ_F": 2.5, "VIX": 30.0},
}

def fetch_snapshot():
    # 주요 지수값 크롤링 (예시: yfinance 기준)
    data = {}
    for key, symbol in SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("regularMarketPrice")
            prev = ticker.info.get("previousClose")
            if price is not None and prev is not None and prev != 0:
                change = price - prev
                pct = (change / prev) * 100
                data[key] = round(pct, 2)
        except Exception as e:
            logging.warning(f"Fail fetch: {key}: {e}")
    return data

def fetch_news():
    # (간단 예시) 연합뉴스 주요 기사 타이틀 5개
    url = "https://www.yna.co.kr/"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [tag.text.strip() for tag in soup.select(".headline-list li a")][:5]
        return titles if titles else ["No news"]
    except Exception as e:
        logging.warning(f"News fetch fail: {e}")
        return ["No news"]

def check_level(data):
    # 레벨별 임계치 경보 판정
    for level in (3, 2, 1):
        for key, th in LEVEL_THRESHOLDS[level].items():
            val = abs(data.get(key, 0))
            if val >= th:
                return level, f"{key}={val} (Lv{level} 이상)"
    return 0, "정상범위"

def make_alarm_message(level, data, news):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return (
        f"[{now}] 센티넬 Lv{level} 경보\n"
        f"지표: {data}\n"
        f"뉴스: {'; '.join(news)}\n"
        f"참고: {', '.join(DATA_SITES)}"
    )

def send_all_alarms(level, data, news):
    msg = make_alarm_message(level, data, news)
    subject = f"Caia 센티넬 Lv{level} 경보"
    filename = f"caia_alert_{datetime.now().strftime('%Y%m%d_%H%M')}_Lv{level}.txt"
    send_codex_email(subject, msg)
    save_to_drive(filename, msg)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    data = fetch_snapshot()
    news = fetch_news()
    level, reason = check_level(data)
    if level > 0:
        send_all_alarms(level, data, news)
        logging.info(f"센티넬 경보 발령 (Lv{level}) — {reason}")
    else:
        logging.info("정상 범위, 경보 없음.")

if __name__ == "__main__":
    main()
