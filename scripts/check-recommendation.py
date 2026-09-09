from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
live=json.loads((ROOT/'content/live-rankings.json').read_text(encoding='utf-8'))
raw=(ROOT/'docs/media-data.js').read_text(encoding='utf-8').strip()
m=re.fullmatch(r'window\.POI_DAYS_MEDIA\s*=\s*(\{.*\});',raw,re.S)
assert m,'media-data.js format changed'
data=json.loads(m.group(1))
rec=data.get('recommendation')

candidates={}
for site_id,site in (live.get('sites') or {}).items():
 if not isinstance(site,dict) or site.get('status')!='ok' or site.get('stale'):continue
 items=site.get('items') or []
 if not items or not isinstance(items[0],dict):continue
 row=items[0]
 if row.get('verified') is True and row.get('title') and row.get('rewardText'):
  candidates[site_id]=row

if candidates:
 assert isinstance(rec,dict),'fresh rankings exist but recommendation is missing'
 assert rec.get('siteId') in candidates,'recommendation site is not a fresh ranking source'
 row=candidates[rec['siteId']]
 assert rec.get('title')==row['title'],'recommendation is not the official #1 item'
 assert rec.get('rewardText')==row['rewardText'],'recommendation reward differs from ranking snapshot'
 html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
 assert rec['title'] in html,'recommendation not rendered into index'
 assert 'POI DAYS独自の優劣順位ではなく' in html,'recommendation basis disclosure missing'
 print('PASS: daily recommendation uses a fresh official #1 ranking item')
else:
 assert rec is None,'recommendation must remain empty when no fresh ranking exists'
 print('PASS: no fresh ranking, recommendation safely remains sample/empty')
