"""Fetch each point site's public ranking once and keep the last good snapshot.

This collector intentionally uses only public, login-free pages.  It validates
at least five rows before replacing a site's previous snapshot.  A failed site
does not erase the last known good data.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from zoneinfo import ZoneInfo
import json
import re

import requests
from bs4 import BeautifulSoup, Tag
from collector_http import fetch_public, official_url

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "live-rankings.json"
TIMEOUT = 15
JST = ZoneInfo("Asia/Tokyo")
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
        "href_hints": ["/item/detail/"],
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

REWARD_RE = re.compile(r"(?:\d[\d,]*(?:\.\d+)?\s*(?:pt|P|ポイント)|\d+(?:\.\d+)?\s*%)", re.I)
RANK_PREFIX_RE = re.compile(r"^\s*(?:第?\s*)?\d{1,2}\s*位?\s*[.．:：\-–—]?\s*")
SPACE_RE = re.compile(r"\s+")


def now_jst() -> datetime:
    return datetime.now(JST)


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
    return fetch_public(url, USER_AGENT, TIMEOUT, minimum=500)


def ranking_html(html: str, source: dict) -> str:
    """Follow only the shopping-ranking URL explicitly advertised by the page."""
    if source['name'] != 'ちょびリッチ':
        return html
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    for node in soup.select('[hx-get][hx-target="#ShopRankingResponse"]'):
        href = urljoin(source['url'], node['hx-get'])
        parsed = urlparse(href)
        query = parse_qs(parsed.query)
        expected = {'logreco[response_number]':['15'], 'logreco[method_type]':['2'],
                    'logreco[spot_name]':['SPShopping_ranking'],
                    'logreco[category1]':['お買い物で貯める']}
        if official_url(source['url'], href) and parsed.path == '/logreco/ranking' and query == expected:
            matches.append(href)
    if len(set(matches)) != 1:
        raise RuntimeError('verified public shopping-ranking endpoint missing or ambiguous')
    return fetch_html(matches[0])


def text(node: Tag) -> str:
    return SPACE_RE.sub(" ", node.get_text(" ", strip=True)).strip()


def reward_text(value: str) -> str | None:
    found = REWARD_RE.findall(value.replace("％", "%"))
    if not found:
        return None
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
    return official_url(base, href)


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
    # Only inspect the verified overall-ranking container. A generic ancestor
    # search can mix neighbouring offers, old rewards and advertising copy.
    selectors = {
        "モッピー": ('ol[data-ga-action="クリック - 総合"] > li', '.a-list__item__title', '.a-list__item__point', 'a.block__link'),
        "ちょびリッチ": ('ul.CommonRankingBox > li.CommonRankingBox__item', '.CommonRankingBox__itemName', '.CommonRankingBox__itemPt', 'a.CommonRankingBox__itemInner'),
        "ワラウ": ('#allPointRanking li', '.sw-AfListCarousel_ListSpecTitle', '.ranking-AfListItem_Pt', 'a.sw-AfListCarousel_AdListLink'),
    }
    if source['name'] in selectors:
        container, title_sel, reward_sel, link_sel = selectors[source['name']]
        rows = []
        for card in soup.select(container)[:5]:
            title, reward, link = card.select_one(title_sel), card.select_one(reward_sel), card.select_one(link_sel)
            if not all((title, reward, link)):
                raise RuntimeError('ranking card missing title, current reward or official link')
            href = urljoin(source['url'], link.get('href', ''))
            if not same_site(source['url'], href) or not href.startswith('https://'):
                raise RuntimeError('ranking card has an invalid official URL')
            if source['name'] == 'ちょびリッチ' and not re.fullmatch(r'/ad_details/\d+', urlparse(href).path):
                raise RuntimeError('invalid Chobirich offer detail URL')
            rows.append({'rank':len(rows)+1, 'title':text(title), 'rewardText':reward_text(text(reward)),
                         'sourceHref':href, 'sample':False, 'verified':True, 'checkedAt':today()})
        return rows
    if soup.select_one('#item-categorized-ranking') or soup.select_one('#ShopRankingResponse'):
        raise RuntimeError('ranking list is loaded dynamically; public HTML has no verifiable top five')
    raise RuntimeError('no verified static ranking container; keeping previous data')


def validate(rows: list[dict], source: dict | None = None) -> None:
    if len(rows) != 5:
        raise RuntimeError(f"expected 5 ranking rows, got {len(rows)}")
    if [row["rank"] for row in rows] != [1, 2, 3, 4, 5]:
        raise RuntimeError("rank sequence is invalid")
    if len({urlparse(r.get('sourceHref', '')).path + '?' + urlparse(r.get('sourceHref', '')).query for r in rows}) != 5:
        raise RuntimeError('duplicate ranking offer URL')
    for row in rows:
        if source and not official_url(source['url'], row.get('sourceHref', '')):
            raise RuntimeError('invalid ranking official URL')
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
            html = ranking_html(fetch_html(source["url"]), source)
            rows = parse_rows(html, source)
            validate(rows, source)
            output["sites"][site_id] = {
                "name": source["name"],
                "scope": "ショッピング" if site_id == "chobirich" else "総合",
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
    print("collector complete; failed sites:", ", ".join(failures) if failures else "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
