"""Validate the narrow permitted changes against the actual task baseline."""
from pathlib import Path
import subprocess,re
R=Path(__file__).resolve().parents[1]
base='4d204a18d2e5afc3514a55b45d164268edbbb12c'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'docs'],text=True,cwd=R).splitlines()
for path in paths:
 if path in ['docs/index.html','docs/sitemap.xml']:continue
 old=subprocess.check_output(['git','show',base+':'+path],cwd=R)
 now=(R/path).read_bytes()
 if path.endswith('.html'):
  expected=old.decode()
  expected=re.sub(r'href="\.\./(?:index\.html)?#(diagnosis|planner|ranking|about|exchange|faq|guide|ways|purpose)"',r'href="../moppy.html#\1"',expected)
  if path=='docs/moppy.html':
   expected=expected.replace('<title>POI DAYS｜あなたに合う、モッピーの始め方。</title>','<title>モッピーの始め方・紹介コード・案件ガイド｜POI DAYS</title>')
   expected=expected.replace('href="https://100things-project.github.io/poi-days/"','href="https://100things-project.github.io/poi-days/moppy.html"').replace('content="https://100things-project.github.io/poi-days/"','content="https://100things-project.github.io/poi-days/moppy.html"').replace('href="#" aria-label="POI DAYS ホーム"','href="index.html" aria-label="POI DAYS ホーム"')
  assert now==expected.encode(),path
 else:assert now==old,path
print('PASS: all baseline assets and pages preserved except explicitly allowed Moppy metadata/home link and moved anchors.')
