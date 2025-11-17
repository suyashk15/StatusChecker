#!/usr/bin/env python3
"""OpenAI status monitor using RSS feed with smart HTTP caching."""

import re
import time
from datetime import datetime, timezone
from typing import Set

import feedparser
import requests

RSS_URL = "https://status.openai.com/history.atom"
POLL_INTERVAL = 30  # seconds


class OpenAIStatusMonitor:
    """Monitors OpenAI status via Atom feed with ETag caching."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.etag: str | None = None
        self.seen_ids: Set[str] = set()

    def run(self) -> None:
        print("Starting OpenAI status monitor (RSS/Atom feed)")
        print(f"Polling every {POLL_INTERVAL}s with HTTP caching...\n")
        
        while True:
            try:
                self._check_updates()
            except KeyboardInterrupt:
                print("\nMonitor stopped by user")
                break
            except Exception as exc:
                print(f"Error: {exc}")
            
            time.sleep(POLL_INTERVAL)

    def _check_updates(self) -> None:
        headers = {}
        if self.etag:
            headers["If-None-Match"] = self.etag

        response = self.session.get(RSS_URL, headers=headers, timeout=10)
        
        if response.status_code == 304:
            # No changes
            return
        
        if response.status_code != 200:
            print(f"HTTP {response.status_code}")
            return

        self.etag = response.headers.get("ETag")
        feed = feedparser.parse(response.content)

        for entry in reversed(feed.entries):
            entry_id = entry.get("id", entry.get("link", ""))
            if entry_id in self.seen_ids:
                continue

            self.seen_ids.add(entry_id)
            title = entry.get("title", "")
            
            # Parse timestamp
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                dt = datetime(*published[:6], tzinfo=timezone.utc)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S%z")
            else:
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")

            # Extract status message
            summary = entry.get("summary", entry.get("content", [{}])[0].get("value", ""))
            # Clean HTML tags
            message = re.sub(r"<[^>]+>", "", summary).strip()
            # Extract just the status line (before "Affected components")
            if "Affected components" in message:
                message = message.split("Affected components")[0].strip()
            # Remove "Status:" prefix if present
            message = re.sub(r"^Status:\s*", "", message).strip()
            if not message:
                message = "No additional details provided."

            print(f"[{timestamp}] Product: {title}")
            print(f"Status: {message}\n")


def main() -> None:
    monitor = OpenAIStatusMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
