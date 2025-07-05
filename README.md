# FGPT Strategy Automation

This repository contains example implementations for automated routines in the FGPT strategy system. Scripts fetch market data and news, generate reports, and back them up to Notion, Google Drive, or email.

## Scripts

- `fgpt_automation.py` – basic morning and night reporting.
- `caia_alert_system.py` – market monitoring with alert levels and strategy suggestions based on the Caia framework. Alerts are pushed to Notion and email when conditions are met.

### Data sources

- [Naver Finance](https://finance.naver.com)
- [Investing.com](https://www.investing.com)
- [Yahoo Finance](https://finance.yahoo.com)
- [CME Group](https://www.cmegroup.com)
- [Bloomberg](https://www.bloomberg.com)
- [Yonhap News](https://www.yna.co.kr)

Both scripts expose a `cloud_handler` function so they can run on serverless platforms such as Cloud Functions or Railway.
Schedules can be customised in each script using the `schedule` library. The UMA/Reflex default times are 23:30, 03:30, 09:30 and 13:30 each day.
