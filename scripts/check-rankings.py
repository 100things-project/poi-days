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
 'chobirich':'/shopping/ad/example-{i}',
}
for site_id,source in mod.SOURCES.items():
 rows=[]
 for i in range(1,6):
  reward=f'{i}.5%' if i==1 else f'{i*1000:,}pt'
  rows.append(f'<li><a href="{hrefs[site_id].format(i=i)}">案件{i}</a><span>{reward}</span></li>')
 html='<html><body><h2>'+source['marker']+'</h2><ol>'+''.join(rows)+'</ol><h2>'+source['stop'][0]+'</h2></body></html>'
 parsed=mod.parse_rows(html,source)
 mod.validate(parsed)
 assert len(parsed)==5,(site_id,parsed)
 assert parsed[0]['title']=='案件1',(site_id,parsed[0])
 assert parsed[0]['rewardText']=='1.5%',(site_id,parsed[0])
 assert parsed[4]['rank']==5

snapshot=json.loads((ROOT/'content/live-rankings.json').read_text(encoding='utf-8'))
assert snapshot['timezone']=='Asia/Tokyo'
assert set(snapshot['sites'])==set(mod.SOURCES)
for site_id,site in snapshot['sites'].items():
 assert site['sourceUrl']==mod.SOURCES[site_id]['url']
 assert isinstance(site['items'],list)
print('PASS: ranking parser fixtures, top-5 validation, percent/point rewards, snapshot schema')
