"""Preserve the current checkout's committed pages, including all newer articles."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','docs'],text=True,cwd=ROOT).splitlines()
# Only the home page and its live-data bundle depend on daily collection/time.
for path in paths:
    if path in {'docs/index.html','docs/media-data.js'}:
        continue
    old=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
    assert (ROOT/path).read_bytes()==old, f'committed page/asset changed: {path}'
for path in ('content/point-sites.json',):
    assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT),path
print('PASS: current HEAD articles, four profiles, referral configuration, sitemap and assets preserved')
