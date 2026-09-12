"""Build Moppy registration-intent search articles without touching legacy pages."""
from pathlib import Path
import html, json, re
ROOT=Path(__file__).resolve().parents[1]
BASE='https://100things-project.github.io/poi-days'
DOCS,DIST=ROOT/'docs',ROOT/'dist'
ARTICLES=[
 ('moppy-referral-code','【2026年9月】モッピー紹介コードはどこ？入力方法・後付け・特典を解説','紹介コード','JOIN SMART','モッピーの紹介コードJh7He170の入力場所、紹介リンクとの違い、後付けできるか、2026年9月の紹介特典を公式情報で解説。登録前に確認したい入力場所、紹介成立の確認方法、5,000Pとの違いまでまとめます。'),
 ('moppy-september-campaign','【2026年9月】モッピー新規登録キャンペーン｜入会特典と条件を解説','9月キャンペーン','SEPTEMBER 2026','2026年9月のモッピー友達紹介・新規登録キャンペーンを解説。紹介された人の30P、条件付き2,000P特典、5,000Pの対象者を整理。期間、達成条件、付与時期、登録前の注意点まで公式情報をもとに確認できます。'),
 ('moppy-pros-cons','モッピーのメリット・デメリット｜登録前に知りたい注意点','メリット・デメリット','BEFORE YOU JOIN','モッピーのメリットとデメリットを公式情報をもとに整理。1P=1円、貯め方や交換先の幅、案件条件、ポイント有効期限など登録前の注意点を解説。向いている人・向いていない人も比較し、登録前の判断材料をまとめます。'),
]
def write_both(rel,text):
 for root in (DOCS,DIST):
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def main():
 template=(ROOT/'content/seo-template.html').read_text(encoding='utf-8').replace('../seo-articles.css','../seo-articles.css?v=20260912-1')
 related={
  'moppy-referral-code':[('moppy-september-campaign','2026年9月のキャンペーン条件'),('moppy-registration','モッピーの登録方法')],
  'moppy-september-campaign':[('moppy-referral-code','紹介コードの入力方法'),('moppy-registration','モッピーの登録方法')],
  'moppy-pros-cons':[('moppy-safety','モッピーの安全性'),('moppy-earning','初心者向けの稼ぎ方')],
 }
 for slug,title,short,label,desc in ARTICLES:
  body=(ROOT/'content/seo'/f'{slug}.html').read_text(encoding='utf-8')
  sections=re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>',body)
  toc='<nav class="seo-toc" aria-label="記事の目次"><strong>この記事で分かること</strong><ol>'+''.join(f'<li><a href="#{sid}">{h}</a></li>' for sid,h in sections)+'</ol></nav>'
  body=body.replace('<section ',toc+'\n<section ',1)
  url=f'{BASE}/articles/{slug}.html'
  vals={'TITLE':html.escape(title),'DESCRIPTION':html.escape(desc,quote=True),'URL':url,'SHORT':short,'LABEL':label,'BODY':body,'CTA_TITLE':'登録前に、もう一つ確認','RELATED':''.join(f'<a href="{s}.html">{t} →</a>' for s,t in related[slug])}
  page=template
  for k,v in vals.items():page=page.replace('{{'+k+'}}',v)
  schema={'@context':'https://schema.org','@graph':[
   {'@type':'Article','headline':title,'description':desc,'mainEntityOfPage':url,'url':url,'datePublished':'2026-09-12','dateModified':'2026-09-12','inLanguage':'ja','author':{'@type':'Organization','name':'POI DAYS'},'publisher':{'@type':'Organization','name':'POI DAYS','url':BASE+'/' }},
   {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'POI DAYS','item':BASE+'/'},{'@type':'ListItem','position':2,'name':title,'item':url}]}
  ]}
  marker='<script src="../analytics.js" defer></script>'
  page=page.replace(marker,'<script type="application/ld+json" data-poidays-schema>'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script>'+marker)
  page=page.replace('../index.html','../')
  write_both('articles/'+slug+'.html',page)
 print('Moppy search cluster built: referral code, September campaign, pros/cons')
if __name__=='__main__':main()
