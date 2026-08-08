"""
Coleta itens publicados nas ultimas HOURS_WINDOW horas nos feeds configurados
em feeds.py e salva em collected.json para a etapa de resumo.
"""

import json
import time
from datetime import datetime, timezone, timedelta

import feedparser

from feeds import FEEDS

HOURS_WINDOW = 26  # margem de 2h sobre as 24h para não perder nada no boundary
OUTPUT_PATH = "collected.json"
MAX_ITEMS_PER_FEED = 15


def entry_datetime(entry):
    for key in ("published_parsed", "updated_parsed"):
        value = getattr(entry, key, None)
        if value:
            return datetime.fromtimestamp(time.mktime(value), tz=timezone.utc)
    return None


def collect():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_WINDOW)
    items = []
    seen_links = set()

    for feed_url in FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as exc:  # feed instavel nao pode derrubar o job inteiro
            print(f"[aviso] falha ao ler {feed_url}: {exc}")
            continue

        source_name = parsed.feed.get("title", feed_url)

        for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
            link = entry.get("link")
            if not link or link in seen_links:
                continue

            published = entry_datetime(entry)
            if published and published < cutoff:
                continue

            items.append(
                {
                    "source": source_name,
                    "title": entry.get("title", "").strip(),
                    "link": link,
                    "summary_raw": entry.get("summary", "").strip(),
                    "published": published.isoformat() if published else None,
                }
            )
            seen_links.add(link)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Coletados {len(items)} itens de {len(FEEDS)} feeds -> {OUTPUT_PATH}")


if __name__ == "__main__":
    collect()
