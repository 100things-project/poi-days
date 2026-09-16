"""Keep the public analytics bundle synchronized from one reviewed source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "analytics.js"
TEXT = SOURCE.read_text(encoding="utf-8")

for folder in (ROOT / "docs", ROOT / "dist"):
    target = folder / "analytics.js"
    target.write_text(TEXT, encoding="utf-8")
    assert target.read_text(encoding="utf-8") == TEXT

print("Analytics bundle synchronized: content -> docs/dist")
