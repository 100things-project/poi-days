"""Build a portable static site. Standard-library Python only."""
from pathlib import Path
import os,re,subprocess,sys,posixpath
from urllib.parse import urlsplit
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'scripts/expand-site.py')],check=True)
d=root/'dist'
site=os.environ.get('SITE_URL','').rstrip('/')
if site:
 u=urlsplit(site)
 if u.scheme not in ('http','https') or not u.netloc or u.query or u.fragment:
  raise SystemExit('SITE_URL must be an http(s) site base URL without query or fragment')
for p in d.rglob('*.html'):
 s=p.read_text()
 s=re.sub(r'<link rel="canonical"[^>]*>','',s)
 def relative(m):
  return m[1]+'="'+posixpath.relpath(m[2].lstrip('/'),p.parent.relative_to(d).as_posix())+'"'
 s=re.sub(r'(href|src)="(/[^"/][^"]*)"',relative,s)
 if site:s=s.replace('</head>',f'<link rel="canonical" href="{site}/{p.relative_to(d).as_posix()}"></head>')
 p.write_text(s)
if site:
 (d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{site}/{p.relative_to(d).as_posix()}</loc></url>' for p in sorted(d.rglob('*.html')))+'</urlset>')
 (d/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+site+'/sitemap.xml\n')
else:
 (d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
 (d/'robots.txt').write_text('User-agent: *\nAllow: /\n')
(d/'.nojekyll').touch()
print('Portable build complete: dist/')
