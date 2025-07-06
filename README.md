# FGPT Strategy Automation

FGPT 전략 시스템 자동화 예시 저장소입니다.  
스크립트는 시장 데이터와 뉴스를 수집하고, 경보/리포트 파일을 이메일, Google Drive, Notion, bochungki(확장채널)로 전송/저장합니다.  
기본 스케줄은 하루 두 차례(09:10, 23:10)이며, `schedule` 라이브러리로 자유롭게 변경할 수 있습니다.

---

## 알림 채널
- **Email**: 경보/리포트가 이메일로 전달
- **Google Drive**: 지정 구글 드라이브에 자동 저장
- **Notion**: 지정 노션 페이지/DB에 알림 기록
- **bochungki**: 커스텀 웹훅/슬랙/텔레그램 등 확장 가능

## 환경 변수
- `NOTION_TOKEN`, `NOTION_PAGE_ID` (노션 연동)
- `GOOGLE_CREDS_JSON` (구글 드라이브 인증 JSON)
- `EMAIL_TO` (이메일 알림 수신 주소)

## Scripts
- `fgpt_automation.py` : 아침/야간 시장 데이터 수집, 리포트 업로드
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
        "https://www.yna.co.kr/"
    ]
)
