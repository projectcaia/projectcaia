"""Lightweight loop for repeated alarms."""

import logging
import time
from alarm_system import send_all_alarms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_monitor(interval: int = 3600) -> None:
    """Send placeholder alarms at a fixed interval."""
    data = {"ping": "ok"}
    news = "[뉴스] 모니터링 중"
    strategy = "[전략] 유지"
    sources = ["https://example.com"]
    while True:
        logging.info("Dispatching monitoring alarm")
        send_all_alarms("loop", 0, data, news, strategy, sources)
        time.sleep(interval)


if __name__ == "__main__":
    run_monitor(600)
