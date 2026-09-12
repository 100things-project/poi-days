"""Preserve committed public files while allowing reviewed generated indexes to expand."""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','docs'],text=True,cwd=ROOT).splitlines()
# The home page/live-data bundle can change with collection. sitemap.xml can
# legitimately gain URLs when reviewed articles are added, so validate it
# separately as a no-loss superset instead of requiring byte-for-byte identity.
for path in paths:
    if path in {'docs/index.html','docs/media-data.js','docs/sitemap.xml'}:
        continue
    old=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
    assert (ROOT/path).read_bytes()==old, f'committed page/asset changed: {path}'

old_sitemap=subprocess.check_output(['git','show','HEAD:docs/sitemap.xml'],cwd=ROOT)
old_root=ET.fromstring(old_sitemap)
new_root=ET.parse(ROOT/'docs/sitemap.xml').getroot()
old_urls={node.text for node in old_root.findall('.//{*}loc') if node.text}
new_urls={node.text for node in new_root.findall('.//{*}loc') if node.text}
assert old_urls <= new_urls, f'sitemap lost committed URLs: {sorted(old_urls-new_urls)}'

for path in ('content/point-sites.json',):
    assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT),path
print('PASS: committed pages/assets preserved; sitemap retained all existing URLs and may add reviewed pages')
