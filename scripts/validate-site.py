from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,subprocess,sys
root=Path(__file__).resolve().parents[1];d=root/'dist'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.h1=0;self.password=False
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.append(a['id'])
  if t=='h1':self.h1+=1
  if t=='input' and a.get('type')=='password':self.password=True
  self.links.extend(a[k] for k in ['href','src'] if k in a)
pages={}
for p in d.rglob('*.html'):
 x=Page();x.feed(p.read_text());pages[p.resolve()]=x
 assert x.h1==1 and not x.password,p
 assert len(x.ids)==len(set(x.ids)),p
 assert '/enrichment.css' in x.links,p
for p,x in pages.items():
 for link in x.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:
   if 'entry/invite.php' in link:assert link=='https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1'
   continue
  target=(d/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path).resolve() if u.path else p
  assert target.exists(),(p,link)
  if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(p,link)
home=(d/'index.html').read_text()
for id in ['mechanism','purpose','ranking','diagnosis','trust','faq','articles']:assert home.count('id="'+id+'"')==1,id
assert home.index('id="ranking"')<home.index('id="diagnosis"')
assert home.count('class="offer-fit"')==5
def digest():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob('*') if p.is_file()}
before=digest();subprocess.run([sys.executable,str(root/'scripts/expand-site.py')],check=True);assert before==digest()
subprocess.run(['node','--check',str(d/'app.js')],check=True)
print(f'PASS {len(pages)} pages: internal links, anchors, referral URLs, unique headings, no password forms, five enhanced cards, repeatable generation, JavaScript syntax')
print('NOT TESTED: browser rendering and runtime interactions at 375px / desktop; static preview unsupported in this environment.')
