"""Add sitemap lastmod only when an article exposes a verified dateModified."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import os
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DIST = ROOT / "dist"
BASE = os.environ.get("SITE_URL", "https://100things-project.github.io/poi-days").rstrip("/")
BASE_URL = urlsplit(BASE)
BASE_PATH = BASE_URL.path.rstrip("/") + "/"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCHEMA_RE = re.compile(r'<script type="application/ld\+json" data-poidays-schema>(.*?)</script>', re.S)
ET.register_namespace("", NS)


def local_html(loc: str) -> Path | None:
    url = urlsplit(loc)
    if url.scheme != BASE_URL.scheme or url.netloc != BASE_URL.netloc:
        return None
    if not url.path.startswith(BASE_PATH):
        return None
    rel = unquote(url.path[len(BASE_PATH):])
    if not rel or rel.endswith("/"):
        rel += "index.html"
    path = DOCS / rel
    return path if path.is_file() else None


def article_modified(path: Path, loc: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = SCHEMA_RE.search(text)
    if not match:
        return None
    try:
        schema = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    items = schema.get("@graph", []) if isinstance(schema, dict) else []
    if isinstance(schema, dict) and schema.get("@type") == "Article":
        items = [schema]
    for item in items:
        if not isinstance(item, dict) or item.get("@type") != "Article":
            continue
        canonical = item.get("url") or item.get("mainEntityOfPage")
        modified = item.get("dateModified")
        if canonical == loc and isinstance(modified, str) and DATE_RE.fullmatch(modified):
            return modified
    return None


def enrich(source: Path) -> bytes:
    tree = ET.parse(source)
    root = tree.getroot()
    added = 0
    for entry in root.findall(f"{{{NS}}}url"):
        loc_node = entry.find(f"{{{NS}}}loc")
        if loc_node is None or not loc_node.text:
            continue
        path = local_html(loc_node.text)
        if path is None:
            continue
        modified = article_modified(path, loc_node.text)
        if not modified:
            continue
        lastmod = entry.find(f"{{{NS}}}lastmod")
        if lastmod is None:
            lastmod = ET.SubElement(entry, f"{{{NS}}}lastmod")
        lastmod.text = modified
        added += 1
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    print(f"Sitemap lastmod added for {added} article URLs")
    return xml + b"\n"


xml = enrich(DOCS / "sitemap.xml")
(DOCS / "sitemap.xml").write_bytes(xml)
(DIST / "sitemap.xml").write_bytes(xml)
assert (DOCS / "sitemap.xml").read_bytes() == (DIST / "sitemap.xml").read_bytes()
