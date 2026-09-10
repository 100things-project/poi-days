"""Collect conservative, public point-site NEWS candidates.

Only items with an explicit official title, date and same-site URL are eligible.
No article body is copied. Failed sources keep their previous good items.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import json
import re
import time

import requests
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "live-news.json"
JST = timezone(timedelta(hours=9))
TIMEOUT = 15
USER_AGENT = "POI-DAYS-NewsBot/1.0 (+https://100things-project.github.io/poi-days/)"

SOURCES = {
    "moppy": {"name": "モッピー", "url": "https://pc.moppy.jp/news/", "path_hints": ["/news/"]},
    "hapitas": {"name": "ハピタス", "url": "https://hapitas.jp/notifications/list", "path_hints": ["/notifications/"]},
    "warau": {"name": "ワラウ", "url": "https://www.warau.jp/service/info/", "path_hints": ["/service/info/permalink/"]},
    "chobirich": {"name": "ちょびリッチ", "url": "https://help.chobirich.com/", "path_hints": ["help.chobirich.com"]},
}

DATE_PATTERNS = [
    re.compile(r"(20\d{2})[年/.-]\s*(\d{1,2})[月/.-]\s*(\d{1,2})日?"),
    re.compile(r"(20\d{2})-(\d{1,2})-(\d{1,2})"),
]
SPACE_RE = re.compile(r"\s+")
CATEGORY_RULES = [
    ("重要", ("重要", "規約", "障害", "不具合", "停止", "終了", "変更", "注意", "詐欺", "メンテナンス")),
    ("キャンペーン", ("キャンペーン", "増量", "ボーナス", "山分け", "プレゼント")),
    ("交換", ("交換", "PayPay", "ドットマネー", "マイル")),
    ("リリース", ("リリース", "新機能", "新アプリ")),
]


def now_iso() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def clean(value: str) -> str:
    return SPACE_RE.sub(" ", value or "").strip()


def parse_date(value: str) -> str | None:
    for pattern in DATE_PATTERNS:
        m = pattern.search(value or "")
        if not m:
            continue
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=JST).date().isoformat()
        except ValueError:
            pass
    return None


def classify(title: str) -> str:
    for category, words in CATEGORY_RULES:
        if any(word in title for word in words):
            return category
    return "お知らせ"


def same_site(base: str, href: str) -> bool:
    a, b = urlparse(base).netloc, urlparse(href).netloc
    return bool(a and b and (a == b or a.endswith("." + b) or b.endswith("." + a)))


def allowed_href(source: dict, href: str) -> bool:
    if not same_site(source["url"], href):
        return False
    parsed = urlparse(href)
    return any(hint in parsed.path or hint in parsed.netloc + parsed.path for hint in source["path_hints"])


def fetch(url: str) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.7", "Cache-Control": "no-cache"}
    error = None
    for attempt in range(2):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            if len(r.text) < 500:
                raise RuntimeError("response too small")
            # Honor HTML charset metadata when HTTP omits it (Warau otherwise
            # defaults to ISO-8859-1 in requests and Japanese dates are lost).
            return BeautifulSoup(r.content, "html.parser").decode()
        except Exception as exc:
            error = exc
            if attempt == 0:
                time.sleep(2)
    raise RuntimeError(str(error))


def nearby_date(anchor: Tag) -> str | None:
    # Search only a small local container, never the whole page.
    node: Tag = anchor
    for _ in range(4):
        txt = clean(node.get_text(" ", strip=True))
        found = parse_date(txt)
        if found:
            return found
        if not isinstance(node.parent, Tag):
            break
        node = node.parent
        if len(clean(node.get_text(" ", strip=True))) > 700:
            break
    return None


def parse_items(html: str, site_id: str, source: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items, seen = [], set()
    if site_id == 'chobirich':
        candidates = []
        for summary in soup.select('details[id] > summary'):
            value = clean(summary.get_text(' ', strip=True))
            date = parse_date(value)
            if not date:
                continue
            title = DATE_PATTERNS[0].sub('', value, count=1).strip()
            candidates.append((title, date, source['url']+'#'+summary.parent['id']))
    else:
        candidates = []
        anchors = soup.select('a[href*="/notifications/detail/"]') if site_id == 'hapitas' else soup.find_all('a', href=True)
        for a in anchors:
            title_node = a.select_one('.serviceInfo-Subject') if site_id == 'warau' else a
            if title_node is None:
                continue
            # A dated sibling belongs to this item; never climb into a list
            # containing multiple links and borrow the first item's date.
            date_node = a.select_one('.serviceInfo-Date')
            if site_id == 'hapitas':
                date_node = a.parent.select_one('.message_date')
                if date_node is None:
                    continue  # duplicate sidebar links have no local date
            date = parse_date(clean(date_node.get_text(' ', strip=True))) if date_node else nearby_date(a)
            candidates.append((clean(title_node.get_text(' ', strip=True)), date, urljoin(source['url'], a['href'])))
    for title, date, href in candidates:
        if len(title) < 8 or len(title) > 180:
            continue
        if not allowed_href(source, href):
            continue
        if not date:
            continue
        key = hashlib.sha256((site_id + "|" + href).encode()).hexdigest()[:20]
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "id": key,
            "site": site_id,
            "siteName": source["name"],
            "date": date,
            "title": title,
            "category": classify(title),
            "sourceUrl": href,
            "official": True,
        })
    items.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
    return items[:20]


def load_previous() -> dict:
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "timezone": "Asia/Tokyo", "generatedAt": None, "items": [], "sources": {}}


def main() -> int:
    previous = load_previous()
    prev_by_site = {}
    for item in previous.get("items", []):
        if isinstance(item, dict) and item.get("site"):
            prev_by_site.setdefault(item["site"], []).append(item)
    collected, source_state = [], {}
    for site_id, source in SOURCES.items():
        try:
            items = parse_items(fetch(source["url"]), site_id, source)
            if not items:
                raise RuntimeError("no dated official news links found")
            collected.extend(items)
            source_state[site_id] = {"name": source["name"], "status": "ok", "fetchedAt": now_iso(), "sourceUrl": source["url"], "count": len(items)}
            print(site_id, "OK", len(items))
        except Exception as exc:
            old = prev_by_site.get(site_id, [])
            collected.extend(old)
            source_state[site_id] = {"name": source["name"], "status": "stale" if old else "unavailable", "fetchedAt": None, "sourceUrl": source["url"], "count": len(old), "lastErrorAt": now_iso(), "lastError": str(exc)[:240]}
            print(site_id, "STALE" if old else "UNAVAILABLE", exc)
    dedup = {item["id"]: item for item in collected if isinstance(item, dict) and item.get("id")}
    items = sorted(dedup.values(), key=lambda x: (x.get("date", ""), x.get("id", "")), reverse=True)[:60]
    output = {"version": 1, "timezone": "Asia/Tokyo", "generatedAt": now_iso(), "items": items, "sources": source_state}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("news collector complete", len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
