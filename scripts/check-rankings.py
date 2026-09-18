"""Offline checks for the daily ranking parser and snapshot schema."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('ranking_fetcher',ROOT/'scripts/fetch-rankings.py')
mod=module_from_spec(spec);spec.loader.exec_module(mod)

hrefs={
 'moppy':'/ad/example-{i}',
 'hapitas':'/item/detail/itemid/{i}',
 'warau':'/contents/point/pointEntrance.php?point_id={i}',
 'chobirich':'/ad_details/{i}',
}
for site_id,source in mod.SOURCES.items():
 rows=[]
 for i in range(1,6):
  reward=f'{i}.5%' if i==1 else f'{i*1000:,}pt'
  if site_id=='moppy':rows.append(f'<li><a class="block__link" href="{hrefs[site_id].format(i=i)}"><h2 class="a-list__item__title">案件{i}</h2><em class="a-list__item__point">{reward}</em></a></li>')
  elif site_id=='hapitas':
   label=f'【最大9,500pt】案件{i}' if i==3 else f'案件{i}'
   rows.append(f'<li><a href="{hrefs[site_id].format(i=i)}">{i} {label} {reward}</a></li>')
  elif site_id=='warau':rows.append(f'<li><a class="sw-AfListCarousel_AdListLink" href="{hrefs[site_id].format(i=i)}"><h3 class="sw-AfListCarousel_ListSpecTitle">案件{i}</h3><p class="ranking-AfListItem_Pt">{reward}</p><div class="sw-AfListItem_BeforePt">999pt</div></a></li>')
  elif site_id=='chobirich':rows.append(f'<li class="CommonRankingBox__item"><a class="CommonRankingBox__itemInner" href="{hrefs[site_id].format(i=i)}"><p class="CommonRankingBox__itemName">案件{i}</p><p class="CommonRankingBox__itemPt">{reward.replace(chr(37),chr(65285))}</p></a></li>')
  else:rows.append(f'<li><a href="{hrefs[site_id].format(i=i)}">案件{i}</a><span>{reward}</span></li>')
 html='<html><body><h2>'+source['marker']+'</h2><ol>'+''.join(rows)+'</ol><h2>'+source['stop'][0]+'</h2></body></html>'
 if site_id=='moppy':html=html.replace('<ol>','<ol data-ga-action="クリック - 総合">')
 if site_id=='chobirich':html=html.replace('<ol>','<ul class="CommonRankingBox">').replace('</ol>','</ul>')
 if site_id=='warau':html=html.replace('<ol>','<ol id="allPointRanking">')
 parsed=mod.parse_rows(html,source)
 mod.validate(parsed)
 assert len(parsed)==5,(site_id,parsed)
 assert parsed[0]['title']=='案件1',(site_id,parsed[0])
 assert parsed[0]['rewardText']=='1.5%',(site_id,parsed[0])
 assert parsed[4]['rank']==5
 if site_id in ('moppy','warau'):assert parsed[1]['rewardText']=='2,000pt',parsed[1]
 if site_id=='hapitas':
  assert parsed[2]['title']=='【最大9,500pt】案件3',parsed[2]
  assert parsed[2]['rewardText']=='3,000pt',parsed[2]
 assert all('999' not in r['rewardText'] for r in parsed)

# Hapitas must stay inside the ranking section and accept only official item-detail links.
hapitas=mod.SOURCES['hapitas']
try:mod.parse_rows('<h2>ランキング</h2><a href="/shopping/promo">宣伝案件 999pt</a><h2>ハピタスチャレンジ</h2>',hapitas)
except RuntimeError:pass
else:raise AssertionError('unverified Hapitas non-ranking offer must fail closed')

snapshot=json.loads((ROOT/'content/live-rankings.json').read_text(encoding='utf-8'))
assert snapshot['timezone']=='Asia/Tokyo'
assert set(snapshot['sites'])==set(mod.SOURCES)
for site_id,site in snapshot['sites'].items():
 assert site['sourceUrl']==mod.SOURCES[site_id]['url']
 assert isinstance(site['items'],list)
print('PASS: ranking parser fixtures, top-5 validation, percent/point rewards, snapshot schema')

# Neither duplicate cards nor cross-origin/credentialed URLs can replace a snapshot.
import copy
for bad_url in ('http://www.chobirich.com/ad_details/1','https://chobirich.com/ad_details/1','https://www.chobirich.com.evil.test/ad_details/1','https://user@www.chobirich.com/ad_details/1','https://www.chobirich.com:444/ad_details/1'):
 bad=copy.deepcopy(parsed);bad[0]['sourceHref']=bad_url
 try:mod.validate(bad,mod.SOURCES['chobirich'])
 except RuntimeError:pass
 else:raise AssertionError(bad_url)
bad=copy.deepcopy(parsed);bad[1]['sourceHref']=bad[0]['sourceHref']
try:mod.validate(bad)
except RuntimeError:pass
else:raise AssertionError('duplicate accepted')
print('PASS: duplicate and unsafe URL rejection')

# Dynamic shopping fragment: direct one-request fetch to the exact public endpoint.
from unittest.mock import patch
source=mod.SOURCES['chobirich']
endpoint=mod.chobirich_ranking_url(source)
with patch.object(mod,'fetch_html',return_value=html) as get:
 session=object()
 result=mod.parse_rows(mod.fetch_chobirich_ranking(source,session=session),source)
 mod.validate(result,source)
 assert get.call_count==1 and get.call_args.args[0]==endpoint
 assert get.call_args.kwargs['session'] is session
 assert get.call_args.kwargs['extra_headers']['HX-Request']=='true'
 assert get.call_args.kwargs['extra_headers']['HX-Target']=='ShopRankingResponse'
 assert get.call_args.kwargs['extra_headers']['Referer']==source['fetch_url']
 assert get.call_args.kwargs['user_agent']==source['request_user_agent']

import copy
for bad in (
 'https://evil.test/logreco/ranking?x=1',
 'https://www.chobirich.com/logreco/other?x=1',
 source['ranking_url'].replace('SPShopping_ranking','OtherRanking'),
):
 bad_source=copy.deepcopy(source);bad_source['ranking_url']=bad
 try:mod.chobirich_ranking_url(bad_source)
 except RuntimeError:pass
 else:raise AssertionError('unverified endpoint accepted: '+bad)
print('PASS: direct public shopping ranking endpoint, one request, strict allowlist')

# Chobirich uses the browser-facing page only as Referer/current URL; the fragment is fetched directly.
assert mod.SOURCES['chobirich']['fetch_url']=='https://www.chobirich.com/shopping'
assert mod.SOURCES['chobirich']['ranking_url'].startswith('https://www.chobirich.com/logreco/ranking?')
assert mod.SOURCES['chobirich']['request_user_agent'].startswith('Mozilla/5.0')
