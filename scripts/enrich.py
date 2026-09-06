"""Progressive editorial enrichment, called after the existing generator."""
import re, json, html
from pathlib import Path

def enrich(root):
 d=root/'dist'; e=html.escape
 offers=json.loads((root/'content/offers.json').read_text())
 def tiles(items,cls='journey-grid'):
  return '<div class="'+cls+'">'+''.join(f'<a class="journey-tile" href="{url}"><span class="tile-number">{i:02}</span><h3>{title}</h3><p>{text}</p><span class="tile-arrow" aria-hidden="true">→</span></a>' for i,(title,text,url) in enumerate(items,1))+'</div>'
 start=tiles([('まず、仕組みを知る','無料登録と、案件ごとの費用は別。','#mechanism'),('自分に合う案件を探す','使いたいサービスから、ひとつ。','#purpose'),('条件を確認して登録','公式の招待ページから始めよう。','/articles/registration.html')])
 purpose=tiles([('無料から検討したい','無料体験の継続料金もチェック。','/articles/categories.html#part-1'),('ゲームを楽しみたい','OS・期限・課金条件の見方から。','/articles/categories.html#part-0'),('還元を活かしたい','買う予定のものを、おトクに。','/guides/rakuten-shopping.html'),('何から始めるか迷う','5つの質問で、無理のない選び方。','#diagnosis')],'purpose-grid')
 mechanism='''<section class="section mechanism" id="mechanism"><div class="container"><p class="eyebrow">HOW IT WORKS</p><h2><span class="phrase">ポイントは、</span><span class="phrase">どこから来るの？</span></h2><div class="money-flow" aria-label="広告費の一部がポイントとして利用者へ還元される仕組み"><div><span>広告主</span><strong>サービスを知ってほしい</strong></div><p>広告費の支払い →</p><div><span>モッピー</span><strong>広告と利用者をつなぐ</strong></div><p>一部を還元 →</p><div><span>あなた</span><strong>条件達成・承認でポイント</strong></div></div><p class="micro">広告を開くだけでは条件達成になりません。広告ごとの条件が優先されます。</p><a class="text-link" href="/articles/about.html">仕組みと費用を詳しく知る →</a></div></section>'''
 trust='''<section class="section trust-panel" id="trust"><div class="container"><p class="eyebrow">BEFORE YOU START</p><h2>安心のために、3つの確認。</h2>'''+tiles([('運営会社を確認','モッピーの運営会社と、当サイトは別です。','/articles/safety.html'),('費用と条件を確認','無料登録＝すべての案件が無料、ではありません。','/articles/categories.html'),('情報源と日付を確認','確認日の記録と、申込時の最新条件を区別。','/articles/policy.html')])+'''<div class="context-cta"><div><h3>登録の前に、気になることを解消。</h3><p>手順と招待コードをまとめて確認できます。</p></div><a class="button outline" href="/articles/registration.html">登録方法を読む →</a></div></div></section>'''
 p=d/'index.html';s=p.read_text()
 s=s.replace('<div class="invite-wrap">','<section class="section first-steps"><div class="container"><p class="eyebrow">FIRST THREE STEPS</p><h2>はじめてなら、この順番で。</h2>'+start+'</div></section><div class="invite-wrap">',1)
 # Move existing ranking earlier instead of adding another copy.
 m=re.search(r'<!-- OFFERS START -->.*?<!-- OFFERS END -->',s,re.S)
 rank=m.group();s=s.replace(rank,'')
 s=s.replace('<section id="about"',mechanism+'<section class="section purpose" id="purpose"><div class="container"><p class="eyebrow">CHOOSE YOUR WAY</p><h2>今日は、どこから始める？</h2>'+purpose+'</div></section>'+rank+'<section id="about"',1)
 # Enrich all five real offer cards; figures remain their original dated record.
 for o in offers:
  marker=f'<a class="button outline" href="guides/{o["id"]}.html">'
  money=f'{o["points"]:,}円相当' if o['points'] else '購入金額に応じた還元'
  info=f'<p class="reward-yen">{money} · 1P＝1円相当</p><div class="offer-fit"><span>こんな人に</span><p>{e(o["fit"])}</p></div><dl class="offer-facts"><div><dt>難易度</dt><dd>未評価</dd></div><div><dt>所要目安</dt><dd>実測なし</dd></div></dl><p class="micro">確認：{e(o["checkedAt"])} ／ 達成期限は上の条件を確認</p>'
  s=s.replace(marker,info+marker,1)
 faqs=[('無料体験は、いつ料金が発生する？','無料期間終了後の継続料金や、有料作品・追加サービスの料金は別に確認します。終了日と解約方法を開始時に控えておきましょう。','/guides/unext.html'),('「予定反映」と「確定反映」は違う？','通帳への予定反映は、ポイント獲得の確定ではありません。獲得条件を達成し、承認されてから交換へ進みます。','/articles/about.html'),('高いポイントの案件から始めるべき？','必要なサービスかどうかを先に判断しましょう。費用・継続契約・期限を含めて比較すると、無理のない案件を選びやすくなります。','/articles/categories.html'),('ゲーム案件は誰でも同じ条件？','OSやインストール履歴などで対象が異なる場合があります。自分の端末で表示される公式条件を確認してください。','/articles/categories.html#part-0'),('このサイトにログインする必要はある？','POI DAYSの解説や診断にログインは不要です。モッピーへの登録・ログインは公式サイトで行います。','/articles/safety.html')]
 extra=''.join(f'<details><summary>{q}</summary><p>{a}</p><a class="text-link" href="{url}">詳しく読む →</a></details>' for q,a,url in faqs)
 s=s.replace('<section id="faq"',trust+'<section id="faq"',1)
 s=re.sub(r'(<section id="faq".*?)(</div></section>)',lambda m:m[1]+extra+m[2],s,count=1,flags=re.S)
 # Clear route from the existing diagnostic result without changing its logic.
 s=s.replace('気になる案件のポイントを試算する →','気になる案件のポイントを試算する →')
 s=s.replace('<a class="text-link" href="#planner">','<a class="text-link" href="#ranking">条件付きの案件一覧を見る →</a><a class="text-link" href="#planner">',1)
 p.write_text(s)
 routes={
 'about':[('仕組みが分かったら','登録画面へ進む前の確認事項。','/articles/registration.html'),('暮らしに合う使い方','費用と時間から選ぶ。','/articles/categories.html')],
 'registration':[('最初の案件を探す','使う予定のサービスから。','/index.html#ranking'),('対象外を防ぐ','始める前に条件を整理。','/articles/categories.html')],
 'safety':[('編集方針を見る','出典・広告表示・更新の考え方。','/articles/policy.html'),('納得したら、登録方法へ','公式での進め方を確認。','/articles/registration.html')],
 'categories':[('買い物の予定がある','楽天市場の経由手順。','/guides/rakuten-shopping.html'),('見たい作品がある','U-NEXTの無料体験と注意点。','/guides/unext.html')]
 }
 for p in d.rglob('*.html'):
  if p.name=='index.html':
   s=p.read_text().replace('</head>','<link rel="stylesheet" href="/enrichment.css"></head>')
   p.write_text(s)
   continue
  s=p.read_text()
  # Replace indiscriminate link lists with related, descriptive navigation cards.
  if p.parent.name=='guides':
   o=next(x for x in offers if x['id']==p.stem)
   related=[(x['name'],x['fit'],'/guides/'+x['id']+'.html') for x in offers if x['id']!=o['id']][:2]
   related.append(('はじめての登録方法','招待コードと登録前の確認。','/articles/registration.html'))
  else:related=routes.get(p.stem,[('仕組みと使い方','自分に合うか確認する。','/articles/about.html'),('登録前の疑問','費用と安全性を確認する。','/articles/safety.html')])
  s=re.sub(r'<div class="related-guides">.*?</div>',tiles(related,'related-grid'),s,flags=re.S)
  if p.stem in routes:
   s=s.replace('<main class="guide-main container narrow">','<main class="guide-main editorial-main container narrow">')
   sections=re.findall(r'<section id="(part-\d+)"><h2>(.*?)</h2>',s)
   toc='<nav class="article-toc" aria-label="記事の目次"><strong>この記事で分かること</strong>'+''.join(f'<a href="#{id}">{title}</a>' for id,title in sections)+'</nav>'
   s=s.replace('<section id="part-0">',toc+'<section id="part-0">',1)
  if p.stem=='categories':
   links=['/index.html#diagnosis','/guides/unext.html','/guides/rakuten-shopping.html','/index.html#ranking','/index.html#diagnosis']
   for i,url in enumerate(links):
    s=re.sub(rf'(<section id="part-{i}">.*?)(</section>)',lambda m:m[1]+f'<a class="text-link" href="{url}">次のガイドを見る →</a>'+m[2],s,count=1,flags=re.S)
  if p.stem in ['policy','privacy']:
   s=re.sub(r'<section><a class="button primary".*?</section>','',s,count=1,flags=re.S)
  s=s.replace('</head>','<link rel="stylesheet" href="/enrichment.css"></head>')
  p.write_text(s)
