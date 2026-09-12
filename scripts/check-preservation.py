"""Preserve committed public files while allowing reviewed generated surfaces to expand."""
from pathlib import Path
import re, subprocess
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','docs'],text=True,cwd=ROOT).splitlines()
MOPPY_GUIDES={
 'docs/articles/moppy-referral-code.html','docs/articles/moppy-september-campaign.html',
 'docs/articles/moppy-pros-cons.html','docs/articles/moppy-safety.html',
 'docs/articles/moppy-reviews.html','docs/articles/moppy-earning.html',
 'docs/articles/moppy-registration.html','docs/articles/moppy-games.html',
}
# The home page/live-data bundle can change with collection. The article hub and
# eight Moppy guides are generated from reviewed source definitions and are
# validated independently by check.py/check-seo.py plus the reproducible-build
# check. moppy.html may only change inside its explicit generated navigation
# marker. sitemap may gain URLs but may not lose committed URLs.
for path in paths:
    if path in {'docs/index.html','docs/media-data.js','docs/articles/index.html','docs/moppy.html','docs/sitemap.xml'} or path in MOPPY_GUIDES:
        continue
    old=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
    assert (ROOT/path).read_bytes()==old, f'committed page/asset changed: {path}'

start='<!-- MOPPY ARTICLE NAV START -->'
end='<!-- MOPPY ARTICLE NAV END -->'
def strip_moppy_nav(text):
    return re.sub(re.escape(start)+r'.*?'+re.escape(end), '', text, flags=re.S)
old_moppy=subprocess.check_output(['git','show','HEAD:docs/moppy.html'],cwd=ROOT,text=True)
new_moppy=(ROOT/'docs/moppy.html').read_text(encoding='utf-8')
assert start in new_moppy and end in new_moppy, 'generated Moppy article navigation missing'
assert strip_moppy_nav(new_moppy)==strip_moppy_nav(old_moppy), 'moppy.html changed outside reviewed article navigation'

# Generated guide bodies are allowed to change when their reviewed source or
# generator changes. Keep minimum structural guards here; detailed metadata,
# referral, link, source and reproducibility checks live in check-seo.py/check.py.
for path in sorted(MOPPY_GUIDES):
    new=(ROOT/path).read_text(encoding='utf-8')
    assert '<section class="seo-next"><h2>次に読む</h2>' in new, f'generated next-reading section missing: {path}'
    assert 'Jh7He170' in new, f'referral marker missing: {path}'
    source_name=Path(path).name
    source=ROOT/'content'/'seo'/source_name
    assert source.exists(), f'reviewed source missing for generated guide: {source_name}'

old_sitemap=subprocess.check_output(['git','show','HEAD:docs/sitemap.xml'],cwd=ROOT)
old_root=ET.fromstring(old_sitemap)
new_root=ET.parse(ROOT/'docs/sitemap.xml').getroot()
old_urls={node.text for node in old_root.findall('.//{*}loc') if node.text}
new_urls={node.text for node in new_root.findall('.//{*}loc') if node.text}
assert old_urls <= new_urls, f'sitemap lost committed URLs: {sorted(old_urls-new_urls)}'

for path in ('content/point-sites.json',):
    assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT),path
print('PASS: committed pages/assets preserved; reviewed generated Moppy guides/navigation allowed; sitemap retained all existing URLs')
