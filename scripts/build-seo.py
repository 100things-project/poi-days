"""Generate the SEO collection without rebuilding the user-edited homepage.

Existing docs is the preserved static base. Only allowlisted article files,
article CSS, and search discovery files are written. No files are deleted.
"""
from pathlib import Path
import html, json, os, re, shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS, DIST = ROOT / 'docs', ROOT / 'dist'
BASE = os.environ.get('SITE_URL', 'https://100things-project.github.io/poi-days').rstrip('/')
u = urlsplit(BASE)
assert u.scheme in ('http', 'https') and u.netloc and not u.query and not u.fragment
ARTICLES = [
 ('moppy-safety', 'モッピーとは？怪しい？安全性・仕組みを初心者向けに解説', '安全性と仕組み', 'UNDERSTAND', 'モッピーが怪しいと感じる初心者へ、広告費からポイントが還元される仕組みと運営会社を解説。安全性の判断材料、個人情報・費用・承認条件の注意点を公式情報で確認し、自分に向いているか考えられます。', ['moppy-reviews','moppy-earning'], '仕組みに納得できたら、条件を確認'),
 ('moppy-reviews', 'モッピーの評判・口コミ｜良い評判と悪い評判を整理', '評判・口コミ', 'COMPARE', 'モッピーの評判が気になる方へ、実在する公開口コミを投稿時期とともに整理。空き時間の活用を評価する声と反映待ちへの不満を公平に紹介し、個人の感想と公式条件を分けて、自分に合う使い方を判断できます。', ['moppy-safety','moppy-registration'], '評判だけでなく、公式条件で判断'),
 ('moppy-earning', 'モッピーの稼ぎ方｜初心者が最初にやること', '初心者の稼ぎ方', 'START SMALL', 'モッピーで何から始めるか迷う初心者へ、買い物・無料コンテンツ・ゲーム・サービス申込の選び方を紹介。クレカなしや短時間で始めるルート、経由忘れを防ぐ確認事項、獲得額を保証しない最初の7日間プランをまとめます。', ['moppy-games','moppy-registration'], '自分に合う始め方が見つかったら'),
 ('moppy-registration', 'モッピーの登録方法｜招待コード・紹介リンクの使い方', '登録方法', 'REGISTRATION', 'モッピーに登録したい方へ、紹介リンクと招待コードJh7He170の使い方を公式案内に沿って解説。登録前の年齢・情報確認、紹介コードの入れ忘れ、特典の反映条件、登録後の確認と退会の疑問まで整理します。', ['moppy-earning','moppy-games'], '入力前に、紹介条件をもう一度確認'),
 ('moppy-games', 'モッピーのゲーム案件｜初心者向けの選び方・注意点', 'ゲーム案件', 'PLAY WISELY', 'モッピーのゲーム案件を始めたい初心者へ、OS・達成条件・期限・課金・判定条件の5項目を解説。開始前の記録、再インストールや機種変更の注意、未反映時の確認手順を整理し、報酬額だけに頼らない選び方を紹介します。', ['moppy-earning','moppy-registration'], 'インストール前に、登録と条件を確認'),
]

def write_both(path, text):
 for directory in (DOCS, DIST):
  p = directory / path
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(text, encoding='utf-8')

def finish_page(page, title=None, description=None, url=None):
 page = page.replace('../index.html', '../')
 if title:
  schema = {'@context':'https://schema.org','@graph':[
   {'@type':'Article','headline':title,'description':description,
    'mainEntityOfPage':url,'url':url,'datePublished':'2026-09-08',
    'dateModified':'2026-09-08','inLanguage':'ja',
    'author':{'@type':'Organization','name':'POI DAYS'},
    'publisher':{'@type':'Organization','name':'POI DAYS','url':BASE+'/'}},
   {'@type':'BreadcrumbList','itemListElement':[
    {'@type':'ListItem','position':1,'name':'POI DAYS','item':BASE+'/'},
    {'@type':'ListItem','position':2,'name':title,'item':url}]}]}
  marker='<script src="../analytics.js" defer></script>'
  page=page.replace(marker,'<script type="application/ld+json" data-poidays-schema>'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script>'+marker)
 return page

def main():
 # Synchronize only known pre-existing publishing differences. Any unexpected
 # difference stops the build rather than choosing a winner for another editor.
 allowed = {'robots.txt','sitemap.xml','exchange-cash.png','exchange-emoney.png',
            'exchange-gift.png','exchange-mile.png','google988181a833d31a3a.html'}
 for p in DOCS.rglob('*'):
  if not p.is_file(): continue
  rel = p.relative_to(DOCS)
  target = DIST / rel
  if not target.exists() or target.read_bytes() != p.read_bytes():
   if str(rel) not in allowed:
    raise SystemExit(f'Unreviewed docs/dist difference: {rel}; reconcile explicitly first.')
   target.parent.mkdir(parents=True, exist_ok=True)
   shutil.copy2(p, target)
 template = (ROOT/'content/seo-template.html').read_text().replace('../seo-articles.css','../seo-articles.css?v=20260908-2')
 titles = {a[0]:a[1] for a in ARTICLES}
 for slug,title,short,label,description,related,cta in ARTICLES:
  assert 90 <= len(description) <= 130, (slug, len(description))
  body = (ROOT/'content/seo'/f'{slug}.html').read_text()
  sections = re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>', body)
  toc = '<nav class="seo-toc" aria-label="記事の目次"><strong>この記事で分かること</strong><ol>' + ''.join(f'<li><a href="#{sid}">{heading}</a></li>' for sid,heading in sections) + '</ol></nav>'
  body = body.replace('<section ', toc+'\n<section ', 1)
  values = dict(TITLE=html.escape(title), DESCRIPTION=html.escape(description,quote=True), URL=BASE+'/articles/'+slug+'.html', SHORT=short, LABEL=label, BODY=body, CTA_TITLE=cta, RELATED=''.join(f'<a href="{r}.html">{titles[r]} →</a>' for r in related))
  page = template
  for key,value in values.items(): page=page.replace('{{'+key+'}}',value)
  write_both('articles/'+slug+'.html',finish_page(page,title,description,values['URL']))
 write_both('seo-articles.css',(ROOT/'content/seo-articles.css').read_text())
 index = template
 body = '<p>知りたいことから選ぶ、モッピーの初心者ガイド。各記事は2026年9月8日に公開情報を確認しています。</p>' + ''.join(f'<a class="seo-index-link" href="{a[0]}.html">{a[1]} →</a>' for a in ARTICLES)
 values = dict(TITLE='モッピー初心者ガイド一覧',DESCRIPTION='モッピーの安全性・評判・稼ぎ方・登録方法・ゲーム案件の選び方をまとめたPOI DAYSの初心者ガイド。',URL=BASE+'/articles/index.html',SHORT='ガイド一覧',LABEL='READ & LEARN',BODY=body,CTA_TITLE='自分に合う始め方を、ひとつずつ',RELATED='<a href="../moppy.html#diagnosis">5問診断で始め方を選ぶ →</a><a href="../moppy.html#ranking">掲載案件と確認日を見る →</a>')
 for key,value in values.items(): index=index.replace('{{'+key+'}}',value)
 write_both('articles/index.html',finish_page(index))
 # Minimal contextual gateways in existing articles; top and guides untouched.
 gateways={'about':'moppy-safety','safety':'moppy-safety','registration':'moppy-registration','categories':'moppy-earning'}
 for old,new in gateways.items():
  page=(DOCS/'articles'/f'{old}.html').read_text()
  page=re.sub(r'<!-- SEO gateway -->.*?<!-- /SEO gateway -->','',page,flags=re.S)
  gateway=f'<!-- SEO gateway --><section><h2>もう少し詳しく知りたい方へ</h2><p><a href="{new}.html">{titles[new]} →</a></p><p><a href="index.html">5つの初心者ガイドから選ぶ →</a></p></section><!-- /SEO gateway -->'
  page=page.replace('</main>',gateway+'</main>')
  write_both('articles/'+old+'.html',page)
 paths=[]
 for p in sorted(DOCS.rglob('*.html')):
  if p.name.startswith('google') or p.name=='qa-preview.html': continue
  source=p.read_text()
  if re.search(r'<meta[^>]+content=["\'][^"\']*noindex',source): continue
  canonical=re.search(r'<link rel="canonical" href="([^"]+)"',source)
  url=canonical[1] if canonical else BASE+'/'+p.relative_to(DOCS).as_posix()
  if url not in paths: paths.append(url)
 paths.sort()
 sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+html.escape(p)+'</loc></url>\n' for p in paths)+'</urlset>\n'
 write_both('sitemap.xml',sitemap)
 write_both('robots.txt','User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
 print(f'SEO build complete: 5 articles + collection; {len(paths)} site pages; existing homepage preserved.')

if __name__ == '__main__': main()
