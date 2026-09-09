"""Fetch each point site's public ranking once and keep the last good snapshot.

This collector intentionally uses only public, login-free pages.  It validates
at least five rows before replacing a site's previous snapshot.  A failed site
does not erase the last known good data.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json
import re
import time

import requests
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "live-rankings.json"
TIMEOUT = 15
USER_AGENT = "POI-DAYS-RankingBot/1.0 (+https://100things-project.github.io/poi-days/)"

SOURCES = {
    "moppy": {
        "name": "モッピー",
        "url": "https://pc.moppy.jp/ad/category_ranking/list.php",
        "marker": "総合",
        "stop": ["無料", "クレカ", "証券", "口座開設", "回線", "ショッピング", "旅行"],
        "href_hints": ["/ad/"],
    },
    "hapitas": {
        "name": "ハピタス",
        "url": "https://hapitas.jp/ranking/",
        "marker": "ランキング",
        "stop": ["ショッピングでためる", "サービスでためる"],
        "href_hints": ["/item/", "/ranking"],
    },
    "warau": {
        "name": "ワラウ",
        "url": "https://www.warau.jp/contents/point/ranking/",
        "marker": "総合TOP10",
        "stop": ["お試しモニターTOP10", "クレジットカードTOP10"],
        "href_hints": ["pointEntrance.php"],
    },
    "chobirich": {
        "name": "ちょびリッチ",
        "url": "https://www.chobirich.com/shopping/",
        "marker": "みんなのランキング",
        "stop": ["今月のキャンペーン情報"],
        "href_hints": ["/ad/", "/shopping/", "/earning/"],
    },
}

REWARD_RE = re.compile(r"(?:\d[\d,]*(?:\.\d+)?\s*(?:P|pt|ポイント)|\d+(?:\.\d+)?\s*%)", re.I)
RANK_PREFIX_RE = re.compile(r"^\s*(?:第?\s*)?\d{1,2}\s*位?\s*[.．:：\-–—]?\s*")
SPACE_RE = re.compile(r"\s+")


def now_jst() -> datetime:
    return datetime.now().astimezone()


def iso_now() -> str:
    return now_jst().isoformat(timespec="seconds")


def today() -> str:
    return now_jst().date().isoformat()


def load_previous() -> dict:
    if not OUT.exists():
        return {"version": 1, "timezone": "Asia/Tokyo", "sites": {}}
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "timezone": "Asia/Tokyo", "sites": {}}


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.7",
        "Cache-Control": "no-cache",
    }
    last = None
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            if len(response.text) < 1000:
                raise RuntimeError("response too small")
            return response.text
        except Exception as exc:
            last = exc
            if attempt == 0:
                time.sleep(2)
    raise RuntimeError(str(last))


def text(node: Tag) -> str:
    return SPACE_RE.sub(" ", node.get_text(" ", strip=True)).strip()


def reward_text(value: str) -> str | None:
    found = REWARD_RE.findall(value)
    if not found:
        return None
    # Some sites expose both a boosted/current value and a baseline value.
    # Preserve what the official ranking row shows instead of guessing which is which.
    unique = []
    for item in found:
        item = SPACE_RE.sub("", item)
        if item not in unique:
            unique.append(item)
    return " / ".join(unique[:2])


def clean_title(value: str) -> str:
    value = RANK_PREFIX_RE.sub("", value)
    value = REWARD_RE.sub("", value)
    value = re.sub(r"★\s*\d(?:\.\d)?(?:\s+\d[\d,]*)?", "", value)
    return SPACE_RE.sub(" ", value).strip(" -｜|:：")


def same_site(base: str, href: str) -> bool:
    try:
        return urlparse(base).netloc.endswith(urlparse(href).netloc) or urlparse(href).netloc.endswith(urlparse(base).netloc)
    except Exception:
        return False


def marker_node(soup: BeautifulSoup, marker: str) -> Tag | None:
    exact = soup.find(string=lambda s: isinstance(s, str) and SPACE_RE.sub(" ", s).strip() == marker)
    if exact and isinstance(exact.parent, Tag):
        return exact.parent
    fuzzy = soup.find(string=lambda s: isinstance(s, str) and marker in SPACE_RE.sub(" ", s))
    return fuzzy.parent if fuzzy and isinstance(fuzzy.parent, Tag) else None


def candidates_from_section(soup: BeautifulSoup, source: dict) -> list[Tag]:
    start = marker_node(soup, source["marker"])
    anchors: list[Tag] = []
    if start:
        for node in start.find_all_next():
            if isinstance(node, Tag):
                node_text = text(node)
                if node.name in {"h1", "h2", "h3"} and any(stop in node_text for stop in source["stop"]):
                    break
                if node.name == "a" and node.get("href"):
                    anchors.append(node)
                if len(anchors) > 100:
                    break
    if not anchors:
        anchors = list(soup.find_all("a", href=True))
    return anchors


def parse_rows(html: str, source: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    seen = set()
    for anchor in candidates_from_section(soup, source):
        href = urljoin(source["url"], anchor.get("href", ""))
        if not same_site(source["url"], href):
            continue
        if source["href_hints"] and not any(hint in href for hint in source["href_hints"]):
            continue
        # Ranking cards often keep the amount outside the link. Read the nearest
        # small card/list container, but cap the amount of surrounding text.
        raw = text(anchor)
        container = anchor
        for _ in range(3):
            parent = container.parent
            if not isinstance(parent, Tag):
                break
            parent_text = text(parent)
            if len(parent_text) <= 350:
                container = parent
                raw = parent_text
            else:
                break
        reward = reward_text(raw)
        if not reward:
            continue
        title = clean_title(text(anchor))
        if len(title) < 2:
            title = clean_title(raw)
        if len(title) < 2 or len(title) > 140:
            continue
        key = re.sub(r"\W", "", title).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append({
            "rank": len(rows) + 1,
            "title": title,
            "rewardText": reward,
            "sourceHref": href,
            "sample": False,
            "verified": True,
            "checkedAt": today(),
        })
        if len(rows) == 5:
            break
    return rows


def validate(rows: list[dict]) -> None:
    if len(rows) != 5:
        raise RuntimeError(f"expected 5 ranking rows, got {len(rows)}")
    if [row["rank"] for row in rows] != [1, 2, 3, 4, 5]:
        raise RuntimeError("rank sequence is invalid")
    for row in rows:
        if not row["title"] or not row["rewardText"] or not row["verified"]:
            raise RuntimeError("ranking row missing required field")


def main() -> int:
    previous = load_previous()
    output = {
        "version": 1,
        "timezone": "Asia/Tokyo",
        "generatedAt": iso_now(),
        "sites": {},
    }
    failures = []
    for site_id, source in SOURCES.items():
        try:
            html = fetch_html(source["url"])
            rows = parse_rows(html, source)
            validate(rows)
            output["sites"][site_id] = {
                "name": source["name"],
                "status": "ok",
                "stale": False,
                "sourceUrl": source["url"],
                "fetchedAt": iso_now(),
                "checkedAt": today(),
                "items": rows,
            }
            print(f"{site_id}: OK ({len(rows)} rows)")
        except Exception as exc:
            failures.append(site_id)
            old = previous.get("sites", {}).get(site_id, {})
            old_items = old.get("items") if isinstance(old, dict) else None
            if isinstance(old_items, list) and len(old_items) >= 5:
                output["sites"][site_id] = {
                    **old,
                    "status": "stale",
                    "stale": True,
                    "lastErrorAt": iso_now(),
                    "lastError": str(exc)[:240],
                }
                print(f"{site_id}: STALE, kept previous snapshot ({exc})")
            else:
                output["sites"][site_id] = {
                    "name": source["name"],
                    "status": "unavailable",
                    "stale": False,
                    "sourceUrl": source["url"],
                    "fetchedAt": None,
                    "checkedAt": None,
                    "items": [],
                    "lastErrorAt": iso_now(),
                    "lastError": str(exc)[:240],
                }
                print(f"{site_id}: UNAVAILABLE ({exc})")
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Individual site failures are non-fatal because stale/placeholder fallback is deliberate.
    print("collector complete; failed sites:", ", ".join(failures) if failures else "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
