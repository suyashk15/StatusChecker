# OpenAI Status Monitor

Lightweight Python script that monitors the official OpenAI status page (`status.openai.com`) using Atom/RSS feeds with smart HTTP caching. Prints new incident updates as soon as they are published.

## Features
- ✅ Event-based monitoring via Atom feed
- ✅ Smart HTTP caching (ETag) for efficiency  
- ✅ Scalable to monitor 100+ status pages
- ✅ Clean console output with timestamps

## Requirements
- Python 3.11+ (for proper SSL support)
- `requests`
- `feedparser`

Install dependencies with:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python status_monitor.py
```

The script polls the Atom feed every 30 seconds using HTTP conditional requests (ETag). Only new, unseen incidents are displayed with their timestamp and status message. Press `Ctrl+C` to stop.

