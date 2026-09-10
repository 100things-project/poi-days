"""Structural checks for the five new articles and preservation of main."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re, subprocess, json
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.h1=0;self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if tag=='h1':self.h1+=1
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a)
titles=[];descriptions=[]
for p in sorted((ROOT/'docs/articles').glob('moppy-*.html')):
 s=p.read_text();page=Page();page.feed(s)
 title=re.search(r'<title>(.*?)</title>',s)[1];titles.append(title)
 description=page.meta['description'];descriptions.append(description)
 assert page.h1==1 and 90<=len(description)<=130
 assert '2026年9月8日' in s and 'Jh7He170' in s
 assert '運営者が報酬を受け取る場合' in s
 assert '<nav class="seo-breadcrumb"' in s and '<nav class="seo-toc"' in s
 schema=json.loads(re.search(r'<script type="application/ld\+json" data-poidays-schema>(.*?)</script>',s)[1])
 assert [x['@type'] for x in schema['@graph']]==['Article','BreadcrumbList']
 assert schema['@graph'][0]['headline']==title.removesuffix('｜POI DAYS')
 assert '../analytics.js' in s and 'poidays_owner_exclude_v1' in s
 assert len(re.findall(r'<a ',s.split('<section class="seo-next">')[1].split('</section>')[0]))==2
 for a in page.links:
  if 'entry/invite' in a['href']:
   assert a['href']=='https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1'
   assert 'sponsored' in a['rel']
  else:
   u=urlsplit(a['href'])
   if not u.scheme:
    target=p.parent/u.path if u.path else p
    assert target.exists(),(p,a['href'])
 assert not re.search(r'私は稼げ|実際にやってみた|絶対稼げる|必ず安全',s)
 print(p.name, 'description:',len(description),'h1:1; sources/date/PR/links:PASS')
assert len(titles)==len(set(titles))==5 and len(set(descriptions))==5
baseline='4d204a1'
for path in ['docs/style.css','docs/visuals.css','docs/visuals-base.css','docs/enrichment.css','docs/app.js','docs/analytics.js','docs/hero-photo.jpeg','docs/google988181a833d31a3a.html']:
 original=subprocess.check_output(['git','show',f'{baseline}:{path}'],cwd=ROOT)
 assert original==(ROOT/path).read_bytes(),path
urls=[n.text for n in ET.parse(ROOT/'docs/sitemap.xml').findall('.//{*}loc')]
assert len(urls)==len(set(urls))==20
assert not any(x.endswith(('/qa-preview.html','/articles/safety.html','/articles/registration.html')) for x in urls)
assert {p.relative_to(ROOT/'docs') for p in (ROOT/'docs').rglob('*') if p.is_file()}=={p.relative_to(ROOT/'dist') for p in (ROOT/'dist').rglob('*') if p.is_file()}
print('PASS: unique metadata, specified referral, baseline shared assets/verification retained; dist/docs file inventory matches')
