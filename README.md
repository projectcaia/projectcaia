# FGPT Strategy Automation

This repository contains example implementations for automated routines in the FGPT strategy system. Scripts fetch market data and news, generate reports, and back them up to Notion, Google Drive, or email.

## Scripts

- `fgpt_automation.py` – basic morning and night reporting.
- `caia_alert_system.py` – market monitoring with alert levels and strategy suggestions based on the Caia framework. Alerts are pushed to Notion and email when conditions are met.

### Data sources

The alert system references several public sites for price and news data:

- Naver Finance
- Investing.com
- Yahoo Finance
- CME Group
- Bloomberg
- Yonhap News

Schedules can be customised in each script using the `schedule` library.
