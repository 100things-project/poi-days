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

# A duplicate sidebar item must not inherit another announcement's date.
hap='<div><a href="/notifications/detail/id/1">最初のお知らせタイトル</a><div class="message_date">2026-06-23</div></div><div><a href="/notifications/detail/id/2">次のお知らせのタイトル</a><div class="message_date">2025-02-20</div></div><aside>2026-06-23<a href="/notifications/detail/id/2">次のお知らせのタイトル</a></aside>'
rows=m.parse_items(hap,'hapitas',m.SOURCES['hapitas'])
assert [(r['date'],r['title']) for r in rows]==[('2026-06-23','最初のお知らせタイトル'),('2025-02-20','次のお知らせのタイトル')]
chobi='<details id="block-a"><summary>2026/9/1【お知らせ】ポイント反映完了</summary><p>本文は取得しない</p></details><a href="/faq">FAQのタイトル 2023/3/1</a>'
rows=m.parse_items(chobi,'chobirich',m.SOURCES['chobirich'])
assert len(rows)==1 and rows[0]['date']=='2026-09-01' and rows[0]['sourceUrl'].endswith('#block-a')
assert '本文' not in rows[0]['title']
print('PASS: no borrowed dates, sidebar duplicates or FAQ-as-news; dated announcement anchors retained')
