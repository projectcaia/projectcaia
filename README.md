# FGPT Strategy Automation

FGPT 전략 시스템 자동화 예시 저장소입니다.  
시장 데이터와 뉴스를 수집, 경보/리포트 파일을 이메일(Google Drive·Gmail)로 전송/저장합니다.  
기본 스케줄은 하루 두 차례(09:10, 23:10)이며, `schedule` 라이브러리로 자유롭게 변경할 수 있습니다.

```bash
pip install -r requirements.txt


```bash
pip install -r requirements.txt
```

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
=======
FGPT 전략 시스템 자동화 예시 저장소입니다.  
스크립트는 시장 데이터와 뉴스를 수집하고, 경보/리포트 파일을 이메일, Google Drive, Notion, bochungki(확장채널)로 전송/저장합니다.  
기본 스케줄은 하루 두 차례(09:10, 23:10)이며, `schedule` 라이브러리로 자유롭게 변경할 수 있습니다.

```markdown
## 알림 채널
- **Email**: 경보/리포트가 이메일로 전달
- **Google Drive**: 지정 구글 드라이브에 자동 저장
- **bochungki**: (커스텀 웹훅/슬랙/텔레그램 등 확장 가능)

## Environment variables
- `EMAIL_TO`: 이메일 알림 수신 주소 (커넥터 연결 시 불필요)
- (필요시) `GOOGLE_CREDS_JSON`: 구글 드라이브 인증 JSON (커넥터 방식이면 불필요)

## Scripts
- `fgpt_automation.py` : 아침/야간 시장 데이터 수집/리포트 업로드
- `caia_alert_system.py` : 센티넬/전략판단 기반 경보 감시
- `codex_monitor.py` : 경량화 감시 루프, 다중 채널 알림

## Data sources
- Naver Finance
- Investing.com
- Yahoo Finance
- CME Group
- Bloomberg
- Yonhap News


## Scheduling

기본 실행: 매일 09:10, 23:10  
`schedule` 라이브러리로 각 스크립트별 실행 시간 커스터마이즈 가능

### Example
```python
from alarm_system import send_all_alarms
send_all_alarms(
    mode="night",
    level=1,
    data={"K200": -1.5, "SP500_F": -1.2, "VIX": 10.5},
    news="[뉴스요약] 야간시장 주요 이슈 ...",
    strategy="[전략판단] 위험관리·관망 추천 ...",
    sources=[
        "https://finance.naver.com/",
        "https://www.investing.com/",
        "https://finance.yahoo.com/",
        "https://www.cmegroup.com/",
        "https://www.bloomberg.com/",
        "https://www.yna.co.kr/"
    ]
)
