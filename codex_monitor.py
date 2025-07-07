# Lightweight sentinel-style monitoring: repeated alarms to Gmail & Google Drive (커넥터 기반)

import logging
import time
from datetime import datetime, time as dtime

# === [1] 알림 채널 (메일/드라이브만 ON) ===
ALARM_CHANNELS = {
    "email": True,
    "drive": True,
    # "notion": False,
    # "bochungki": False,
}

# === [2] 커넥터 알림 함수 ===
def send_codex_email(subject, content):
    codex.send_email(subject=subject, content=content)

def save_to_drive(filename, content):
    codex.save_drive(filename=filename, content=content)

# === [3] 메시지 포맷 ===
def make_alarm_message(mode, level, data, news, strategy, sources):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return (
        f"[{now}] ({mode}) Lv{level} 감시 리포트\n"
        f"지표: {data}\n뉴스: {news}\n전략: {strategy}\n"
        f"참고: {', '.join(sources)}"
    )

def send_all_alarms(mode, level, data, news, strategy, sources):
    msg = make_alarm_message(mode, level, data, news, strategy, sources)
    subject = f"{mode.upper()} Lv{level} 감시 알림"
    filename = f"codex_{mode}_alarm_{datetime.now().strftime('%Y%m%d_%H%M')}_Lv{level}.txt"
    if ALARM_CHANNELS.get("email"):
        send_codex_email(subject, msg)
    if ALARM_CHANNELS.get("drive"):
        save_to_drive(filename, msg)

# === [4] 임계치/데이터/뉴스/전략 샘플 ===
LEVEL_CONDITIONS = {
    1: {"K200": 1.2, "SP500_F": 1.0, "NASDAQ_F": 1.0, "VIX_KR": 7, "VIX": 7},
    2: {"K200": 2.0, "SP500_F": 1.8, "NASDAQ_F": 1.8, "VIX_KR": 15, "VIX": 15},
    3: {"K200": 3.0, "SP500_F": 2.5, "NASDAQ_F": 2.5, "VIX_KR": 30, "VIX": 30},
}

DATA_SOURCES = [
    "https://finance.naver.com/",
    "https://www.investing.com/",
    "https://finance.yahoo.com/",
    "https://www.cmegroup.com/",
    "https://www.bloomberg.com/",
    "https://www.yna.co.kr/"
]

def fetch_indicators():
    # TODO: 실제 API 연동 or 임시 샘플 데이터
    return {
        "K200": -1.5,
        "VIX_KR": 8.1,
        "SP500_F": -1.2,
        "NASDAQ_F": -1.3,
        "VIX": 10.5
    }

def fetch_news_summary(mode, level, data):
    # TODO: 실제 뉴스 API/크롤러 연동
    return "[뉴스요약] 최근 이슈/헤드라인..."

def generate_strategy_judgment(mode, level, data):
    # TODO: 전략 코멘트 생성
    return "[전략판단] 위험관리 및 관망 권고"

def check_level(data, mode):
    # 기본: 임계치 기준 레벨 자동 판별
    targets = ["K200", "SP500_F", "NASDAQ_F", "VIX_KR", "VIX"]
    for lvl in sorted(LEVEL_CONDITIONS.keys(), reverse=True):
        cond = LEVEL_CONDITIONS[lvl]
        for key in targets:
            if abs(data.get(key, 0)) >= cond.get(key, 99):
                return lvl
    return 0

# === [5] 메인 루프 ===
def main_loop(interval=3600):
    while True:
        now = datetime.now()
        mode = "night" if now.hour >= 18 or now.hour < 6 else "domestic"
        data = fetch_indicators()
        level = check_level(data, mode)
        if level > 0:
            news = fetch_news_summary(mode, level, data)
            strategy = generate_strategy_judgment(mode, level, data)
            send_all_alarms(mode, level, data, news, strategy, DATA_SOURCES)
            logging.info(f"Sentinel Lv{level} alarm sent: {data}")
        else:
            logging.info("No alert condition met.")
        time.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    main_loop(3600)  # 1시간마다 실행 (테스트 후 조정 가능)
