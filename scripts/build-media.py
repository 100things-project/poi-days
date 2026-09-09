"""Render the mobile-first media index; retain the separate Moppy page."""
from pathlib import Path
from html import escape as e
import copy,json,os

ROOT=Path(__file__).resolve().parents[1]
base_data=json.loads((ROOT/'content/media-home.json').read_text(encoding='utf-8'))
data=copy.deepcopy(base_data)
live_path=ROOT/'content/live-rankings.json'
live={}
if live_path.exists():
 try: live=json.loads(live_path.read_text(encoding='utf-8'))
 except Exception: live={}

def write(path,text):
 for folder in ['docs','dist']:
  (ROOT/folder/path).write_text(text,encoding='utf-8')

def image(src,alt,cls='',w=900,h=600):
 return f'<img src="{e(src,quote=True)}" alt="{e(alt,quote=True)}" class="{cls}" width="{w}" height="{h}" loading="lazy">'

def verified_rows(site_id):
 site=(live.get('sites') or {}).get(site_id) or {}
 rows=site.get('items') if site.get('status') in {'ok','stale'} else []
 if not isinstance(rows,list) or len(rows)<5:return None
 checked=site.get('checkedAt')
 result=[]
 for row in rows[:5]:
  if not isinstance(row,dict) or not row.get('verified') or not row.get('title') or not row.get('rewardText') or not checked:return None
  result.append({
   'title':row['title'],
   'category':'公式ランキング',
   'sample':False,
   'verified':True,
   'rewardText':row['rewardText'],
   'checkedAt':checked,
   'sourceHref':row.get('sourceHref'),
   'href':None,
   'image':'visuals/about.svg'
  })
 return result

for site in data.get('sites',[]):
 rows=verified_rows(site['id'])
 if rows:data['rankings'][site['id']]=rows

data['rankingMeta']={}
for site in data.get('sites',[]):
 state=(live.get('sites') or {}).get(site['id']) or {}
 data['rankingMeta'][site['id']]={
  'status':state.get('status','sample'),
  'stale':bool(state.get('stale')),
  'checkedAt':state.get('checkedAt'),
  'sourceUrl':state.get('sourceUrl')
 }

def ranks(rows):
 if not rows:return '<li class="empty-state">現在準備中です。</li>'
 html=[]
 for i,r in enumerate(rows[:5]):
  verified=r.get('sample') is False and r.get('verified') is True and r.get('rewardText') and r.get('checkedAt')
  amount=e(str(r.get('rewardText'))) if verified else 'サンプル'
  small=e(r.get('checkedAt'))+' 確認' if verified else '金額未掲載'
  html.append(f'<li class="ranking-row"><span class="rank-number">{i+1}</span>'+image(r.get('image') or 'visuals/about.svg','ランキング掲載案件のイメージ','rank-thumb',42,42)+f'<div class="rank-description"><h3>{e(r["title"])}</h3><span class="rank-category">{e(r.get("category") or "公式ランキング")}</span></div><div class="rank-amount">{amount}<small>{small}</small></div></li>')
 return ''.join(html)

moppy_meta=data['rankingMeta'].get('moppy',{})
if moppy_meta.get('checkedAt'):
 disclosure='各ポイントサイトの公開ランキングを毎日取得しています。'
 if moppy_meta.get('stale'):disclosure+=' 一部は前回取得分です。'
else:
 disclosure='サンプル表示 · 自動取得は本番反映前です。'

page=(ROOT/'content/media-home.html').read_text(encoding='utf-8')
values={
'TABS':''.join(f'<button type="button" id="tab-{s["id"]}" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="ranking-panel" tabindex="{0 if i==0 else -1}" data-site="{s["id"]}">{e(s["name"])}</button>' for i,s in enumerate(data['sites'])),
'RANKINGS':ranks(data['rankings'].get('moppy',[])),
'RANKING_DISCLOSURE':e(disclosure),
'ARTICLES':''.join(f'<a class="article-row" href="{e(a["href"])}">'+image(a['image'],'記事のテーマを表すイメージ')+f'<div><h3>{e(a["title"])}</h3><time datetime="{a["date"]}">{a["date"].replace("-",".")}</time></div><span class="arrow" aria-hidden="true">›</span></a>' for a in data['articles']),
'NEWS':''.join(f'<li><span class="news-date">サンプル</span><span>{e(n["title"])}</span></li>' for n in data['news'])}
features=[]
for f in data['features']:
 tag='a' if f['href'] else 'div';attrs=f' href="{e(f["href"])}"' if f['href'] else ''
 features.append(f'<{tag} class="feature"{attrs}>'+ (image(f['image'],f['title']+'のイメージ') if f['image'] else '')+f'<div class="feature-copy"><small>{e(f["label"])}</small><h3>{e(f["title"])}</h3><p>{e(f["description"])}</p></div></{tag}>')
values['FEATURES']=''.join(features)
if not data['articles']:values['ARTICLES']='<p class="empty-state">記事は現在準備中です。</p>'
if not data['news']:values['NEWS']='<li>ニュースは現在準備中です。</li>'
if not data['features']:values['FEATURES']='<p class="empty-state">特集は現在準備中です。</p>'
for k,v in values.items():page=page.replace('{{'+k+'}}',v)
base=os.environ.get('SITE_URL','https://100things-project.github.io/poi-days').rstrip('/')
page=page.replace('https://100things-project.github.io/poi-days/',base+'/')
write('index.html',page)
write('media-data.js','window.POI_DAYS_MEDIA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
for name in ['media-home.css','media-home.js']:write(name,(ROOT/'content'/name).read_text(encoding='utf-8'))
print('Media build complete: live ranking snapshot merged when verified; docs/dist synchronized.')
