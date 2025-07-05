import os
import logging
from datetime import datetime
import schedule
import time
import requests
import yfinance as yf
from bs4 import BeautifulSoup

from notion_client import Client as NotionClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Credentials
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
EMAIL_TO = os.getenv("EMAIL_TO")

notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# Reference sites for data collection and news parsing
DATA_SITES = {
    "naver_finance": "https://finance.naver.com/",
    "investing": "https://www.investing.com/",
    "yahoo_finance": "https://finance.yahoo.com/",
    "cme_group": "https://www.cmegroup.com/",
    "bloomberg": "https://www.bloomberg.com/",
    "yonhap": "https://www.yna.co.kr/",
}

# --- Market symbols ---
SYMBOLS = {
    "KOSPI200": "^KS200",
    "SP500_FUT": "ES=F",
    "NASDAQ_FUT": "NQ=F",
    "US_VIX": "^VIX",
    "USD_INDEX": "DX-Y.NYB",
}

# Thresholds for alert levels
LEVEL_THRESHOLDS = {
    1: {
        "KOSPI200": 2.2,
        "SP500_FUT": 1.2,
        "NASDAQ_FUT": 1.2,
        "KOR_VIX": 7.0,
        "US_VIX": 7.0,
    },
    2: {
        "KOSPI200": 3.5,
        "SP500_FUT": 2.0,
        "NASDAQ_FUT": 2.0,
        "KOR_VIX": 15.0,
        "US_VIX": 15.0,
    },
    3: {
        "KOSPI200": 5.0,
        "SP500_FUT": 3.0,
        "NASDAQ_FUT": 3.0,
        "KOR_VIX": 30.0,
        "US_VIX": 30.0,
    },
}

NEWS_KEYWORDS = {
    2: ["급락", "패닉", "매도세", "공포"],
    3: ["서킷브레이커", "VI 발동", "거래중단", "긴급", "위기", "폭락"],
}


def fetch_headlines(url, selector):
    """Return a list of text headlines from the given URL using CSS selector."""
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        return [tag.get_text(strip=True) for tag in soup.select(selector)][:5]
    except Exception as e:
        logging.warning(f"Failed to fetch headlines from {url}: {e}")
        return []


def fetch_news_bloomberg():
    return fetch_headlines(DATA_SITES["bloomberg"], "h3")


def fetch_news_yonhap():
    return fetch_headlines(DATA_SITES["yonhap"], "a.tit")


# Placeholder for Korea VIX as yfinance does not provide it directly
# In production, replace with an actual data source

def fetch_kor_vix():
    return None  # TODO: implement data fetch


def fetch_naver_index(code: str):
    """Fetch index data from Naver Finance."""
    try:
        url = f"https://finance.naver.com/sise/sise_index.nhn?code={code}"
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("span#now_value")
        rate_tag = soup.select_one("span#change_rate")
        if price_tag and rate_tag:
            price = float(price_tag.text.replace(",", ""))
            pct = float(rate_tag.text.replace("%", "").replace(",", ""))
            return price, pct
    except Exception as e:
        logging.warning(f"Failed to fetch Naver index {code}: {e}")
    return None, None


def fetch_market_data():
    logging.info("Fetching market data...")
    data = {}
    for name, symbol in SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get("regularMarketPrice")
            prev = info.get("previousClose")
            if price is not None and prev:
                pct = (price - prev) / prev * 100.0
                data[name] = {
                    "price": price,
                    "change_pct": pct,
                }
        except Exception as e:
            logging.warning(f"Failed to fetch {name}: {e}")

    # Attempt additional fetch for KOSPI200 from Naver Finance
    if "KOSPI200" not in data:
        price, pct = fetch_naver_index("KPI200")
        if price is not None:
            data["KOSPI200"] = {"price": price, "change_pct": pct}
    kor_vix = fetch_kor_vix()
    if kor_vix is not None:
        data["KOR_VIX"] = kor_vix
    return data


def fetch_news():
    logging.info("Fetching news...")
    news = []
    news.extend(fetch_news_bloomberg())
    news.extend(fetch_news_yonhap())
    if not news:
        news = ["No headlines"]
    return news


def check_alert_level(market_data, news_list):
    level = 0
    triggers = []
    # Check market thresholds
    for lvl in [3, 2, 1]:
        for key, th in LEVEL_THRESHOLDS[lvl].items():
            info = market_data.get(key)
            if info:
                pct = info.get("change_pct")
                if pct is not None and abs(pct) >= th:
                    level = max(level, lvl)
                    triggers.append(f"{key} {pct:.2f}%")
        # Check news keywords
        if lvl in NEWS_KEYWORDS:
            for n in news_list:
                for kw in NEWS_KEYWORDS[lvl]:
                    if kw in n:
                        level = max(level, lvl)
                        triggers.append(f"News keyword '{kw}'")
        if level >= lvl:
            break
    return level, triggers


def generate_strategy(level):
    if level == 0:
        return "정상 범위 내 변동. 모니터링 유지."
    if level == 1:
        return "주의 단계입니다. 변동성 확대 구간 모니터링을 강화하고 리스크 관리를 점검하세요."
    if level == 2:
        return "경계 단계입니다. 일부 포지션 축소와 헤지 전략을 고려하십시오."
    if level >= 3:
        return "위험 단계입니다. 포지션을 대폭 축소하고 안전 자산 비중을 높이는 긴급 대응이 필요합니다."
    return ""


def generate_report(market_data, level, triggers, news_list):
    lines = [f"알림 시각: {datetime.now().isoformat()}"]
    lines.append(f"경보 레벨: {level}")
    if triggers:
        lines.append("트리거: " + ", ".join(triggers))
    lines.append("\n[시장 지표]")
    for key, info in market_data.items():
        if isinstance(info, dict):
            lines.append(f"- {key}: {info['price']} ({info['change_pct']:.2f}%)")
    lines.append("\n[뉴스]")
    for n in news_list:
        lines.append(f"- {n}")
    lines.append("\n[카이아 전략 분석]")
    lines.append(generate_strategy(level))
    return "\n".join(lines)


def save_to_notion(content):
    if notion and NOTION_PAGE_ID:
        logging.info("Saving alert to Notion...")
        notion.pages.create(
            parent={"page_id": NOTION_PAGE_ID},
            properties={},
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"text": [{"type": "text", "text": {"content": content}}]}
            }]
        )


def send_email(content):
    if EMAIL_TO:
        logging.info("Sending alert via email...")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        if smtp_server and smtp_user and smtp_pass:
            try:
                import smtplib
                from email.mime.text import MIMEText

                msg = MIMEText(content)
                msg["Subject"] = "Caia Alert"
                msg["From"] = smtp_user
                msg["To"] = EMAIL_TO

                with smtplib.SMTP_SSL(smtp_server) as s:
                    s.login(smtp_user, smtp_pass)
                    s.sendmail(smtp_user, [EMAIL_TO], msg.as_string())
            except Exception as e:
                logging.warning(f"Failed to send email: {e}")
        else:
            logging.info("SMTP credentials not set; email not sent")


def monitor(session_name):
    logging.info(f"Monitoring session: {session_name}")
    market_data = fetch_market_data()
    news_list = fetch_news()
    level, triggers = check_alert_level(market_data, news_list)
    if level > 0:
        report = generate_report(market_data, level, triggers, news_list)
        save_to_notion(report)
        send_email(report)
        logging.info(report)
    else:
        logging.info("No alert conditions met.")


def schedule_jobs():
    schedule.every().day.at("09:05").do(monitor, session_name="regular")
    schedule.every().day.at("18:05").do(monitor, session_name="night")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    logging.info("Starting Caia alert system...")
    schedule_jobs()
