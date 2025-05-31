# Telegram API Credentials Fetcher

This script automates the process of obtaining your Telegram `api_id` and `api_hash` from https://my.telegram.org using Playwright.

## Requirements
- Python 3.8+
- Google Chrome or Chromium browser

## Installation
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Usage
```bash
python telegram_parser.py
```

You will be prompted to enter your phone number and the confirmation code sent to your Telegram app.

## Notes
- The script opens a visible browser window for you to interact with Telegram's website.
- No credentials are stored.
- For any issues, screenshots of errors are saved in the `error_screenshots` directory. 
