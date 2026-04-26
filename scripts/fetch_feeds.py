import json
import hashlib
import html
import re
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

import feedparser
import requests
from dateutil import parser as date_parser


BASE_DIR = Path(__file__).resolve().parents[1]
FEEDS_JSON = BASE_DIR / "data" / "feeds.json"
OUT_DIR = BASE_DIR / "docs"
OUT_JSON = OUT_DIR / "items.json"
OUT_RSS = OUT_DIR / "feed.xml"

TITLE_PREFIX_LEN = 20
MAX_ITEMS = 300


def normalize_title(title: str) -> str:
    title = title or ""
    title = html.unescape(title)
    title = re.sub(r"\s+", "", title)
    title = title.replace("　", "")
    return title.strip()


def dedupe_key(title: str) -> str:
    normalized = normalize_title(title)
    prefix = normalized[:TITLE_PREFIX_LEN]
    return hashlib.sha256(prefix.encode("utf-8")).hexdigest()


def parse_date(entry) -> datetime:
    candidates = [
        getattr(entry, "published", None),
        getattr(entry, "updated", None),
        getattr(entry, "created", None),
    ]

    for value in candidates:
        if value:
            try:
                dt = date_parser.parse(value)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass

    return datetime.now(timezone.utc)


def fetch_feed(feed):
    url = feed["url"]
    feed_title = feed.get("feed_title", "")

    headers = {
        "User-Agent": "CustomFeedFilter/1.0"
    }

    res = requests.get(url, headers=headers, timeout=20)
    res.raise_for_status()

    parsed = feedparser.parse(res.content)

    items = []

    for entry in parsed.entries:
        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()

        if not title or not link:
            continue

        published_dt = parse_date(entry)

        items.append({
            "title": title,
            "title_prefix": normalize_title(title)[:TITLE_PREFIX_LEN],
            "link": link,
            "published": published_dt.isoformat(),
            "published_rss": format_datetime(published_dt),
            "feed_title": feed_title,
            "source_feed_url": url,
            "dedupe_key": dedupe_key(title),
        })

    return items


def build_rss(items):
    now = datetime.now(timezone.utc)

    lines = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        '<rss version="2.0">',
        '<channel>',
        '<title>Filtered Economic Reports</title>',
        '<link>https://example.com/</link>',
        '<description>Deduplicated feed generated from multiple economic report feeds</description>',
        f'<lastBuildDate>{format_datetime(now)}</lastBuildDate>',
    ]

    for item in items:
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        feed_title = html.escape(item["feed_title"])
        guid = html.escape(item["dedupe_key"])

        description = html.escape(
            f'Feed: {item["feed_title"]} / Prefix: {item["title_prefix"]}'
        )

        lines.extend([
            "<item>",
            f"<title>{title}</title>",
            f"<link>{link}</link>",
            f"<guid isPermaLink=\"false\">{guid}</guid>",
            f"<pubDate>{item['published_rss']}</pubDate>",
            f"<category>{feed_title}</category>",
            f"<description>{description}</description>",
            "</item>",
        ])

    lines.extend([
        "</channel>",
        "</rss>",
    ])

    return "\n".join(lines)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    feeds = json.loads(FEEDS_JSON.read_text(encoding="utf-8"))

    all_items = []

    for feed in feeds:
        try:
            print(f'Fetching: {feed.get("feed_title")} - {feed["url"]}')
            all_items.extend(fetch_feed(feed))
        except Exception as e:
            print(f'ERROR: {feed["url"]} - {e}')

    # 新しい順
    all_items.sort(key=lambda x: x["published"], reverse=True)

    # タイトル前20文字が完全一致なら重複扱い
    deduped = {}
    for item in all_items:
        key = item["dedupe_key"]
        if key not in deduped:
            deduped[key] = item

    items = list(deduped.values())
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    OUT_JSON.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    OUT_RSS.write_text(
        build_rss(items),
        encoding="utf-8"
    )

    print(f"Generated: {OUT_JSON}")
    print(f"Generated: {OUT_RSS}")
    print(f"Items: {len(items)}")


if __name__ == "__main__":
    main()