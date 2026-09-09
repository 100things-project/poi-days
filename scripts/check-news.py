from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import tempfile,json
p=Path('scripts/fetch-news.py');spec=spec_from_file_location('news',p);m=module_from_spec(spec);spec.loader.exec_module(m)
html='''<html><body><div><span>2026年9月9日</span><a href="/news/123">【重要】ポイント交換条件変更のお知らせ</a></div><div><span>2026-09-08</span><a href="/news/124">9月キャンペーン開催のお知らせ</a></div></body></html>'''
source={'name':'モッピー','url':'https://pc.moppy.jp/news/','path_hints':['/news/']}
rows=m.parse_items(html,'moppy',source)
assert len(rows)==2,rows
assert rows[0]['date']=='2026-09-09' and rows[0]['official'] is True
assert rows[0]['category']=='重要'
assert rows[1]['category']=='キャンペーン'
assert all(r['sourceUrl'].startswith('https://pc.moppy.jp/news/') for r in rows)
assert m.parse_date('2026年2月30日') is None
assert not m.same_site('https://pc.moppy.jp/','https://evil.example/')
print('PASS: news parser date/title/source/category/same-site guards')
