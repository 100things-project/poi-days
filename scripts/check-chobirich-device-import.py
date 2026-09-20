"""Offline tests for the device-supplied Chobirich ranking importer."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import json

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ranking = load("ranking_fetcher_for_device_test", ROOT / "scripts" / "fetch-rankings.py")
ingest = load("ranking_device_ingest", ROOT / "scripts" / "import-chobirich-ranking.py")

def fragment(duplicate=False, external=False):
    cards = []
    for i in range(1, 6):
        href = f"/ad_details/{1 if duplicate and i == 2 else i}"
        if external and i == 1:
            href = "https://evil.example/ad_details/1"
        cards.append(
            '<li class="CommonRankingBox__item">'
            f'<a class="CommonRankingBox__itemInner" href="{href}">'
            f'<p class="CommonRankingBox__itemName">端末案件{i}</p>'
            f'<p class="CommonRankingBox__itemPt">{i}%</p>'
            '</a></li>'
        )
    padding = "<!--" + ("x" * 700) + "-->"
    return (padding + '<ul class="CommonRankingBox">' + "".join(cards) + "</ul>").encode("utf-8")

with TemporaryDirectory() as td:
    td = Path(td)
    snapshot = json.loads((ROOT / "content" / "live-rankings.json").read_text(encoding="utf-8"))
    original_other = {k: copy.deepcopy(v) for k, v in snapshot["sites"].items() if k != "chobirich"}
    out = td / "live-rankings.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ingest.OUT = out

    good = td / "good.html"
    good.write_bytes(fragment())
    rows = ingest.import_fragment(good)
    assert len(rows) == 5
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["sites"]["chobirich"]["status"] == "ok"
    assert result["sites"]["chobirich"]["stale"] is False
    assert result["sites"]["chobirich"]["captureMethod"] == "device-public-fragment"
    assert result["sites"]["chobirich"]["items"][0]["title"] == "端末案件1"
    assert result["sites"]["chobirich"]["items"][4]["rewardText"] == "5%"
    for site_id, old in original_other.items():
        assert result["sites"][site_id] == old, site_id

    # Re-seed before every rejection case so a failure cannot hide a mutation.
    for label, payload in [
        ("duplicate", fragment(duplicate=True)),
        ("external", fragment(external=True)),
        ("undersized", b"<html>tiny</html>"),
        ("oversized", b"x" * 65_536),
    ]:
        out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        candidate = td / f"{label}.html"
        candidate.write_bytes(payload)
        before = out.read_bytes()
        try:
            ingest.import_fragment(candidate)
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"{label} device payload was accepted")
        assert out.read_bytes() == before, f"{label} failure mutated snapshot"

print("PASS: device Chobirich import is top-5 validated, fail-closed and preserves other sites")
