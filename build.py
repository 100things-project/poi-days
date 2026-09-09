"""Build a portable static site. Standard-library Python only."""
from pathlib import Path
import os,re,subprocess,sys,posixpath,shutil
from urllib.parse import urlsplit
root=Path(__file__).resolve().parent
# The published layout has direct user edits not represented by the legacy
# layout generator. Default builds must preserve them (including verification
# files). Keep the old generator available only through an explicit opt-in.
if '--legacy-layout-build' not in sys.argv:
 subprocess.run([sys.executable,str(root/'scripts/build-media.py')],check=True)
 subprocess.run([sys.executable,str(root/'scripts/build-seo.py')],check=True)
 raise SystemExit(0)
subprocess.run([sys.executable,str(root/'scripts/expand-site.py')],check=True)
d=root/'dist'
site=os.environ.get('SITE_URL','https://100things-project.github.io/poi-days').rstrip('/')
if site:
 u=urlsplit(site)
 if u.scheme not in ('http','https') or not u.netloc or u.query or u.fragment:
  raise SystemExit('SITE_URL must be an http(s) site base URL without query or fragment')
ga_id='G-0TZ7EH65BW'
ga_tag=(f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>'
        '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
        f"gtag('js',new Date());gtag('config','{ga_id}');</script>")
for p in d.rglob('*.html'):
 s=p.read_text()
 s=re.sub(r'<link rel="canonical"[^>]*>','',s)
 def relative(m):
  return m[1]+'="'+posixpath.relpath(m[2].lstrip('/'),p.parent.relative_to(d).as_posix())+'"'
 s=re.sub(r'(href|src)="(/[^"/][^"]*)"',relative,s)
 if ga_id not in s:
  s=s.replace('</head>',ga_tag+'</head>')
 if p.relative_to(d).as_posix()=='articles/privacy.html':
  s=s.replace('独自のアクセス解析、広告配信タグ、問い合わせフォームは設置していません。パスワードや認証コードを当サイトへ入力する必要はありません。','当サイトではGoogle Analytics 4を利用してアクセス状況を計測します。Googleに送信される情報の取り扱いはGoogleのポリシーに従います。広告配信タグや問い合わせフォームは現在設置していません。パスワードや認証コードを当サイトへ入力する必要はありません。')
  s=s.replace('最終更新：2026年9月6日。','最終更新：2026年9月7日。')
 if site:s=s.replace('</head>',f'<link rel="canonical" href="{site}/{p.relative_to(d).as_posix()}"></head>')
 p.write_text(s)
if site:
 (d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{site}/{p.relative_to(d).as_posix()}</loc></url>' for p in sorted(d.rglob('*.html')))+'</urlset>')
 (d/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+site+'/sitemap.xml\n')
else:
 (d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
 (d/'robots.txt').write_text('User-agent: *\nAllow: /\n')
(d/'.nojekyll').touch()
docs=root/'docs'
if docs.exists(): shutil.rmtree(docs)
shutil.copytree(d,docs)
print('Portable build complete: dist/')
