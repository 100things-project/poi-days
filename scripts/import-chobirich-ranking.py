"""Import one Chobirich public ranking fragment supplied by a user device.

The device only supplies the login-free HTML response.  All parsing, URL
allowlisting and top-five validation stay in this repository before any data is
saved or published.
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "live-rankings.json"

spec = spec_from_file_location("ranking_fetcher", ROOT / "scripts" / "fetch-rankings.py")
ranking = module_from_spec(spec)
spec.loader.exec_module(ranking)

MIN_BYTES = 500
MAX_BYTES = 65_535
SUPPORTED_ENCODINGS = ("utf-8", "cp932")


def load_snapshot() -> dict:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    if data.get("timezone") != "Asia/Tokyo" or not isinstance(data.get("sites"), dict):
        raise RuntimeError("invalid ranking snapshot")
    if set(data["sites"]) != set(ranking.SOURCES):
        raise RuntimeError("ranking snapshot site set changed")
    return data


def decode_fragment(raw: bytes) -> tuple[str, str]:
    if not (MIN_BYTES <= len(raw) <= MAX_BYTES):
        raise RuntimeError(f"unexpected Chobirich fragment size: {len(raw)} bytes")
    for encoding in SUPPORTED_ENCODINGS:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise RuntimeError("Chobirich fragment is neither UTF-8 nor CP932/Shift_JIS")


def import_fragment(path: Path) -> list[dict]:
    raw = path.read_bytes()
    html, encoding = decode_fragment(raw)

    source = ranking.SOURCES["chobirich"]
    rows = ranking.parse_rows(html, source)
    ranking.validate(rows, source)

    data = load_snapshot()
    data["generatedAt"] = ranking.iso_now()
    data["sites"]["chobirich"] = {
        "name": source["name"],
        "scope": "ショッピング",
        "status": "ok",
        "stale": False,
        "sourceUrl": source["url"],
        "fetchedAt": ranking.iso_now(),
        "checkedAt": ranking.today(),
        "captureMethod": "device-public-fragment",
        "captureEncoding": encoding,
        "items": rows,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: import-chobirich-ranking.py <fragment.html>")
    rows = import_fragment(Path(sys.argv[1]))
    print(f"chobirich: DEVICE IMPORT OK ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
