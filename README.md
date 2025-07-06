# FGPT Strategy Automation

FGPT 전략 시스템 자동화 루틴 예시 저장소입니다. 시장 데이터와 뉴스를 수집해 경보와 보고서를 생성하며, 이메일·Google Drive·Notion·bochungki(확장 알림)로 전송합니다. 기본 스케줄은 하루 두 차례(09:10, 23:10)이며 `schedule` 라이브러리로 자유롭게 조정할 수 있습니다.

## FGPT 감시 자동화 구조
- **센티넬**: 실시간 지표를 감시하여 이상 변동을 탐지합니다.
- **뉴스 리플렉스**: 주요 기사와 이벤트를 요약해 전략 판단에 반영합니다.
- **경보 루틴**: 레벨별 경보 메시지를 만들어 여러 채널로 발송합니다.

## 알림 채널
Reports and alerts can be delivered through the following channels:
- **Email**
- **Google Drive**
- **Notion**
- **bochungki** (custom webhook or future expansion)

### Environment variables
Set these variables so the scripts can authenticate with external services:
- `NOTION_TOKEN`, `NOTION_PAGE_ID` – Notion credentials
- `GOOGLE_CREDS_JSON` – Google Drive service account key
- `EMAIL_TO` – address for email alerts


## Scripts
- `fgpt_automation.py`: Runs the morning and night routines to gather data and upload reports.
- `caia_alert_system.py`: Monitors markets and issues strategy alerts in the Caia framework.
- `codex_monitor.py`: Lightweight sentinel loop that dispatches alarms to all channels.
- `alarm_system.py`: Helper module that formats alert messages and sends them through the available channels.

## Data sources
The automation examples reference the following public sites:
- Naver Finance
- Investing.com
- Yahoo Finance
- CME Group
- Bloomberg
- Yonhap News

## Scheduling
The default configuration schedules tasks with `schedule.every().day.at("09:10")` and `schedule.every().day.at("23:10")`. You can customise the run times in each script.

Example usage of the alarm system:
```python
from alarm_system import send_all_alarms

send_all_alarms(
    mode="night",
    level=2,
    data={"K200": -1.5, "SP500_F": -1.2, "VIX": 10.5},
    news="[뉴스요약] 야간시장 급변 이슈 ...",
    strategy="[전략판단] 위험관리, 헷지 추천 ...",
    sources=[
        "https://finance.naver.com/",
        "https://www.investing.com/",
        "https://finance.yahoo.com/",
        "https://www.cmegroup.com/",
        "https://www.bloomberg.com/",
        "https://www.yna.co.kr/",
    ],
)
```

