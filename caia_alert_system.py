"""Market monitoring and strategy alerts."""

import logging
from datetime import datetime
import yfinance as yf
from alarm_system import send_all_alarms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def fetch_snapshot() -> dict:
    """Return basic market snapshot using yfinance."""
    k200 = yf.Ticker("^KS200").info.get("regularMarketPrice")
    sp500_f = yf.Ticker("ES=F").info.get("regularMarketPrice")
    vix = yf.Ticker("^VIX").info.get("regularMarketPrice")
    return {"K200": k200, "SP500_F": sp500_f, "VIX": vix}


def monitor_and_alert() -> None:
    data = fetch_snapshot()
    news = "[뉴스] 데이터 수집 예시"
    strategy = "[전략] 시장 상황 점검"
    sources = [
        "https://finance.naver.com/",
        "https://www.investing.com/",
        "https://finance.yahoo.com/",
    ]
    send_all_alarms("monitor", 1, data, news, strategy, sources)


if __name__ == "__main__":
    logging.info("Running CAIA alert system")
    monitor_and_alert()
