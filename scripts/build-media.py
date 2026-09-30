"""Render the mobile-first media index; retain the separate Moppy page."""
from pathlib import Path
from html import escape as e
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import copy,json,os,re

ROOT=Path(__file__).resolve().parents[1]
base_data=json.loads((ROOT/'content/media-home.json').read_text(encoding='utf-8'))
data=copy.deepcopy(base_data)

def load_json(path):
 try:return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
 except Exception:return {}

live=load_json(ROOT/'content/live-rankings.json')
live_news=load_json(ROOT/'content/live-news.json')
point_sites=(load_json(ROOT/'content/point-sites.json').get('sites') or [])

def write(path,text):
 for folder in ['docs','dist']:
  (ROOT/folder/path).write_text(text,encoding='utf-8')

def image(src,alt,cls='',w=900,h=600):
 return f'<img src="{e(src,quote=True)}" alt="{e(alt,quote=True)}" class="{cls}" width="{w}" height="{h}" loading="lazy">'

def official_href(value, source):
 try:
  url,base=urlparse(value or ''),urlparse(source or '')
  return value if url.scheme=='https' and url.hostname==base.hostname else None
 except ValueError:return None

def title_markup(value):
 pattern=r'(使い方|登録方法|招待コード|紹介リンク|初心者|最初|ゲーム案件|選び方|注意点|安全性|仕組み|評判|口コミ)'
 return ''.join('<span class="title-phrase">'+e(p)+'</span>' if re.fullmatch(pattern,p) else e(p) for p in re.split(pattern,value) if p)

def verified_rows(site_id):
 site=(live.get('sites') or {}).get(site_id) or {}
 rows=site.get('items') if site.get('status') in {'ok','stale'} else []
 if not isinstance(rows,list) or len(rows)<5:return None
 checked=site.get('checkedAt')
 result=[]
 for row in rows[:5]:
  if not isinstance(row,dict) or not row.get('verified') or not row.get('title') or not row.get('rewardText') or not checked:return None
  result.append({'title':row['title'],'category':('公式ショッピング順位' if site.get('scope')=='ショッピング' else '公式ランキング'),'sample':False,'verified':True,'rewardText':row['rewardText'],'checkedAt':checked,'sourceHref':row.get('sourceHref'),'href':official_href(row.get('sourceHref'),site.get('sourceUrl')),'image':'visuals/about.svg'})
 return result

for site in data.get('sites',[]):
 rows=verified_rows(site['id'])
 if rows:data['rankings'][site['id']]=rows

data['rankingMeta']={}
for site in data.get('sites',[]):
 state=(live.get('sites') or {}).get(site['id']) or {}
 old_date=bool(state.get('checkedAt') and state['checkedAt'] < datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat())
 data['rankingMeta'][site['id']]={'status':state.get('status','sample'),'stale':bool(state.get('stale') or old_date),'checkedAt':state.get('checkedAt'),'sourceUrl':state.get('sourceUrl')}

def ranks(rows):
 if not rows:return '<li class="empty-state">現在準備中です。</li>'
 html=[]
 for i,r in enumerate(rows[:5]):
  verified=r.get('sample') is False and r.get('verified') is True and r.get('rewardText') and r.get('checkedAt')
  amount=e(str(r.get('rewardText'))) if verified else 'サンプル';small='公式掲載' if verified else '金額未掲載'
  title=e(r['title'])
  if verified and r.get('href'):title=f'<a href="{e(r["href"],quote=True)}" target="_blank" rel="noopener noreferrer">{title}</a>'
  html.append(f'<li class="ranking-row"><span class="rank-number">{i+1}</span>'+image(r.get('image') or 'visuals/about.svg','ランキング掲載案件のイメージ','rank-thumb',42,42)+f'<div class="rank-description"><h3>{title}</h3><span class="rank-category">{e(r.get("category") or "公式ランキング")}</span></div><div class="rank-amount">{amount}<small>{small}</small></div></li>')
 return ''.join(html)

moppy_meta=data['rankingMeta'].get('moppy',{})
if moppy_meta.get('checkedAt'):
 disclosure=moppy_meta['checkedAt']+' 取得 · 各ポイントサイトの公開ランキング'
 if moppy_meta.get('stale'):disclosure+=' 一部は前回取得分です。'
else:disclosure='サンプル表示 · 今回の取得結果は未掲載です。'

safe_news=[]
for n in live_news.get('items') or []:
 if not isinstance(n,dict) or n.get('official') is not True:continue
 if not all(isinstance(n.get(k),str) and n.get(k) for k in ['date','title','siteName','sourceUrl']):continue
 if not n['sourceUrl'].startswith('https://'):continue
 safe_news.append(n)
safe_news=sorted(safe_news,key=lambda x:(x['date'],x.get('id','')),reverse=True)[:6]
if safe_news:
 data['news']=safe_news
 news_note='公式お知らせを1日1回取得します。日付は公式の掲載日です。取得できないサイトは前回データを保持します。'
 missing=[s.get('name',sid) for sid,s in (live_news.get('sources') or {}).items() if s.get('status')!='ok']
 if missing:news_note+=' 今回未取得：'+ '・'.join(missing)+'。'
else:news_note='サンプル表示 · 公式NEWSの自動取得は本番反映前です。'

# Today's featured offer is deliberately not a cross-site "best" comparison.
# Among sites whose ranking was freshly and successfully fetched, rotate through
# each site's official #1 so different point sites get fair exposure.
def daily_recommendation():
 candidates=[]
 today=datetime.now(ZoneInfo('Asia/Tokyo')).date()
 site_names={s['id']:s['name'] for s in data.get('sites',[])}
 for site_id,site in (live.get('sites') or {}).items():
  if not isinstance(site,dict) or site.get('status')!='ok' or site.get('stale'):continue
  if site.get('checkedAt')!=today.isoformat():continue
  items=site.get('items') or []
  if not items or not isinstance(items[0],dict):continue
  row=items[0]
  if not official_href(row.get('sourceHref'),site.get('sourceUrl')):continue
  if row.get('verified') is not True or not row.get('title') or not row.get('rewardText'):continue
  candidates.append({'siteId':site_id,'siteName':site_names.get(site_id,site.get('name',site_id)),'title':row['title'],'rewardText':row['rewardText'],'checkedAt':site.get('checkedAt'),'sourceHref':row.get('sourceHref')})
 if not candidates:return None
 candidates.sort(key=lambda x:x['siteId'])
 today=datetime.now(ZoneInfo('Asia/Tokyo')).date()
 return candidates[today.toordinal()%len(candidates)]

recommendation=daily_recommendation()
data['recommendation']=recommendation

page=(ROOT/'content/media-home.html').read_text(encoding='utf-8')
if recommendation:
 href=recommendation.get('sourceHref') if isinstance(recommendation.get('sourceHref'),str) and recommendation['sourceHref'].startswith('https://') else None
 tag='a' if href else 'div'
 href_attr=f' href="{e(href,quote=True)}" target="_blank" rel="noopener noreferrer"' if href else ''
 rec_html=(
  '<section class="media-section recommendations" id="recommendations" aria-labelledby="recommendation-title">'
  '<div class="section-heading"><h1 id="recommendation-title"><span class="section-icon" aria-hidden="true">✦</span>今日のおすすめ案件</h1><span class="status">公式ランキングから</span></div>'
  f'<{tag} class="lead-story"{href_attr}><div class="lead-image">'
  '<img src="visuals/way-shopping.webp" width="900" height="600" alt="今日の注目案件のイメージ" fetchpriority="high">'
  f'<span class="image-label">{e(recommendation["siteName"])}</span></div><div class="lead-copy">'
  '<p class="eyebrow">各サイト公式ランキング1位から日替わりで紹介</p>'
  f'<h2>{e(recommendation["title"])}</h2><p>{e(str(recommendation["rewardText"]))}</p>'
  f'<span class="story-link">{e(recommendation["siteName"])}の公式掲載を見る <span aria-hidden="true">→</span></span></div></{tag}>'
  f'<p class="section-note">{e(recommendation.get("checkedAt") or "")}確認。POI DAYS独自の優劣順位ではなく、取得できた各サイトの公式1位案件から日替わりで紹介しています。</p></section>'
 )
 page=re.sub(r'<section class="media-section recommendations" id="recommendations".*?</section>',rec_html,page,count=1,flags=re.S)

point_site_links=[]
for site in point_sites:
 sid=site.get('id');name=site.get('name');target=site.get('page')
 if not sid or not name or not target:continue
 point_site_links.append(f'<li><a href="{e(target,quote=True)}" aria-label="{e(name)}の特徴を見る"><span class="site-name {e(sid,quote=True)}">{e(name)}</span><small>特徴を見る →</small></a></li>')

values={
'POINT_SITES':''.join(point_site_links),
'TABS':''.join(f'<button type="button" id="tab-{s["id"]}" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="ranking-panel" tabindex="{0 if i==0 else -1}" data-site="{s["id"]}">{e(s["name"])}</button>' for i,s in enumerate(data['sites'])),
'RANKINGS':ranks(data['rankings'].get('moppy',[])),'RANKING_DISCLOSURE':e(disclosure),'NEWS_NOTE':e(news_note),
'ARTICLES':''.join(f'<a class="article-row" href="{e(a["href"])}">'+image(a['image'],'記事のテーマを表すイメージ')+f'<div><h3>{title_markup(a["title"])}</h3><time datetime="{a["date"]}">{a["date"].replace("-",".")}</time></div><span class="arrow" aria-hidden="true">›</span></a>' for a in data['articles'])}
if safe_news:
 values['NEWS']=''.join(f'<li><span class="news-date">{e(n["date"].replace("-","."))}</span><span><small>{e(n.get("siteName") or "公式")}</small> <a href="{e(n["sourceUrl"],quote=True)}" target="_blank" rel="noopener noreferrer">{e(n["title"])}</a></span></li>' for n in safe_news)
else:
 values['NEWS']=''.join(f'<li><span class="news-date">サンプル</span><span>{e(n["title"])}</span></li>' for n in data['news'])
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
print('Media build complete: verified rankings, daily featured offer, real point-site links and official NEWS merged when available; docs/dist synchronized.')
