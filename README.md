# FGPT Strategy Automation

This repository contains an example implementation of an automated routine for the FGPT strategy system. The script collects market data and news, generates reports, and backs them up to external services (Notion, Google Drive, email). Scheduling is done twice daily: after the main market opens and after the night session.

A separate `alarm_system.py` module demonstrates how to format alert messages and send them to multiple channels (email, Google Drive, Notion, or a custom webhook). Credentials such as `NOTION_TOKEN` and `NOTION_PAGE_ID` should be provided via environment variables.
