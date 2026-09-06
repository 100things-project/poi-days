from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import hashlib,subprocess,sys
root=Path(__file__).resolve().parent;d=root/'dist'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.headings=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.append(a['id'])
  if t=='h1':self.headings+=1
  if t=='img':assert a.get('alt') and a.get('width') and a.get('height')
  self.links.extend(a[k] for k in ['src','href'] if k in a)
pages={}
for p in d.rglob('*.html'):
 x=Page();x.feed(p.read_text());pages[p.resolve()]=x
 assert x.headings==1 and len(x.ids)==len(set(x.ids)),p
for p,x in pages.items():
 for link in x.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:
   if 'entry/invite.php' in link:assert link=='https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1'
   continue
  assert not u.path.startswith('/'),(p,link)
  target=(p.parent/u.path).resolve() if u.path else p
  assert target.exists(),(p,link)
  if u.fragment and target in pages:assert u.fragment in pages[target].ids,(p,link)
for p in (d/'visuals').glob('*.svg'):ET.parse(p)
def hashes():return {str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob('*') if p.is_file()}
before=hashes();subprocess.run([sys.executable,str(root/'build.py')],check=True);assert before==hashes()
print(f'PASS: {len(pages)} pages, relative links, anchors, referral URLs, image dimensions, SVG XML, reproducible build')
