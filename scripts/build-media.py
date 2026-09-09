"""Render the mobile-first media index; retain the separate Moppy page."""
from pathlib import Path
from html import escape as e
import json,os,re
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'content/media-home.json').read_text())
def write(path,text):
 for folder in ['docs','dist']:
  (ROOT/folder/path).write_text(text)
def image(src,alt,cls='',w=900,h=600):
 return f'<img src="{e(src,quote=True)}" alt="{e(alt,quote=True)}" class="{cls}" width="{w}" height="{h}" loading="lazy">'
def ranks(rows):
 if not rows:return '<li class="empty-state">現在準備中です。</li>'
 return ''.join(f'<li class="ranking-row"><span class="rank-number">{i+1}</span>'+image(r['image'],'掲載カテゴリのイメージ','rank-thumb',42,42)+f'<div class="rank-description"><h3>{e(r["title"])}</h3><span class="rank-category">{e(r["category"])}</span></div><div class="rank-amount">サンプル<small>金額未掲載</small></div></li>' for i,r in enumerate(rows[:5]))
page=(ROOT/'content/media-home.html').read_text()
values={
'TABS':''.join(f'<button type="button" id="tab-{s["id"]}" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="ranking-panel" tabindex="{0 if i==0 else -1}" data-site="{s["id"]}">{e(s["name"])}</button>' for i,s in enumerate(data['sites'])),
'RANKINGS':ranks(data['rankings'].get('moppy',[])),
'ARTICLES':''.join(f'<a class="article-row" href="{e(a["href"])}">'+image(a['image'],'記事のテーマを表すイメージ')+f'<div><h3>{e(a["title"])}</h3><time datetime="{a["date"]}">{a["date"].replace("-",".")}</time></div><span class="arrow" aria-hidden="true">›</span></a>' for a in data['articles']),
'NEWS':''.join(f'<li><span class="news-date">サンプル</span><span>{e(n["title"])}</span></li>' for n in data['news'])}
features=[]
for f in data['features']:
 tag='a' if f['href'] else 'div'
 attrs=f' href="{e(f["href"])}"' if f['href'] else ''
 features.append(f'<{tag} class="feature"{attrs}>'+ (image(f['image'],f['title']+'のイメージ') if f['image'] else '')+f'<div class="feature-copy"><small>{e(f["label"])}</small><h3>{e(f["title"])}</h3><p>{e(f["description"])}</p></div></{tag}>')
values['FEATURES']=''.join(features)
if not data['articles']: values['ARTICLES']='<p class="empty-state">記事は現在準備中です。</p>'
if not data['news']: values['NEWS']='<li>ニュースは現在準備中です。</li>'
if not data['features']: values['FEATURES']='<p class="empty-state">特集は現在準備中です。</p>'
for k,v in values.items():page=page.replace('{{'+k+'}}',v)
base=os.environ.get('SITE_URL','https://100things-project.github.io/poi-days').rstrip('/')
page=page.replace('https://100things-project.github.io/poi-days/',base+'/')
write('index.html',page)
write('media-data.js','window.POI_DAYS_MEDIA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
for name in ['media-home.css','media-home.js']:write(name,(ROOT/'content'/name).read_text())
print('Media build complete: mobile index, static fallback, replaceable data; docs/dist synchronized.')
