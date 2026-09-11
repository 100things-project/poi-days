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
 if site_id == 'hapitas':
  try:mod.parse_rows('<a href="/shopping/promo">宣伝案件 999pt</a>',source)
  except RuntimeError:pass
  else:raise AssertionError('unverified non-ranking must fail closed')
  continue
 rows=[]
 for i in range(1,6):
  reward=f'{i}.5%' if i==1 else f'{i*1000:,}pt'
  if site_id=='moppy':rows.append(f'<li><a class="block__link" href="{hrefs[site_id].format(i=i)}"><h2 class="a-list__item__title">案件{i}</h2><em class="a-list__item__point">{reward}</em></a></li>')
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
 assert all('999' not in r['rewardText'] for r in parsed)

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

# Dynamic shopping fragment: one request to the URL advertised by official HTML.
from urllib.parse import urlencode
from unittest.mock import patch
query=urlencode({'logreco[response_number]':'15','logreco[method_type]':'2','logreco[spot_name]':'SPShopping_ranking','logreco[category1]':'お買い物で貯める'})
endpoint='https://www.chobirich.com/logreco/ranking?'+query
parent=f'<button hx-get="{endpoint}" hx-target="#ShopRankingResponse">総合</button>'
with patch.object(mod,'fetch_html',return_value=html) as get:
 result=mod.parse_rows(mod.ranking_html(parent,mod.SOURCES['chobirich']),mod.SOURCES['chobirich'])
 mod.validate(result,mod.SOURCES['chobirich'])
 assert get.call_count==1 and get.call_args.args[0]==endpoint
with patch.object(mod,'fetch_html',side_effect=AssertionError('unsafe request')):
 for unsafe in (parent.replace('www.chobirich.com','evil.test'),parent.replace('SPShopping_ranking','OtherRanking'),'<div id="ShopRankingResponse"></div>'):
  try:mod.ranking_html(unsafe,mod.SOURCES['chobirich'])
  except RuntimeError:pass
  else:raise AssertionError('unverified endpoint accepted')
print('PASS: public shopping endpoint discovery, one request, fail closed on source changes')
