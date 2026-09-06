from pathlib import Path
import json,re,html
root=Path(__file__).resolve().parents[1]; d=root/'dist'; e=html.escape
import subprocess,sys
(d/'index.html').write_text((root/'content/home-template.html').read_text())
subprocess.run([sys.executable,str(root/'scripts/build-guides.py')],check=True)
invite='https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1'
cta=f'<a class="button primary" href="{e(invite)}" target="_blank" rel="sponsored noopener">モッピーを無料で始める →</a><p class="micro">招待コード：Jh7He170 · 特典には条件があります。</p>'
articles={
'about':('モッピーとは？ポイントの貯め方と仕組み','買い物やサービス利用の前に、モッピーを経由。条件を満たし承認されると、ポイントを受け取れるサービスです。',[
('どうしてポイントがもらえるの？','広告主からの広告費の一部が利用者へ還元される仕組みです。広告を開くだけで、すべての案件のポイントが付くわけではありません。'),('日常の予定から選ぶ','買う予定のある商品や使いたいサービスから選びましょう。獲得ポイントより出費が大きければ、節約になるとは限りません。'),('無料登録と無料案件は別','モッピーへの会員登録は無料。広告には購入・契約・課金が必要なものもあります。無料体験では終了後の料金も確認してください。'),('ポイントが使えるまで','広告を経由 → 条件達成 → 通帳で承認確認 → 交換の順です。1Pは1円相当ですが、交換先によって最低ポイント・手数料・反映日数が違います。')]),
'registration':('モッピーの登録方法・招待コード','登録はモッピー公式の画面で行います。このサイトでは会員情報を入力・送信しません。',[
('1 招待ページを開く','下の招待リンクから公式ページへ。紹介特典の対象者・期限・達成条件を先に確認します。'),('2 画面に表示された方法で登録','公式の案内に沿ってメールアドレスなどを登録し、認証手続きを進めます。画面の項目は変更されることがあるため、表示される説明を優先してください。'),('3 招待コードを確認','コードの入力を求められたら Jh7He170 を使用します。招待リンク経由でも、特典の適用条件は登録先で確認してください。'),('4 登録内容と規約を確認','入力内容を確認し、規約・プライバシーポリシーを読んでから登録を完了します。パスワードや認証コードを第三者に伝えないでください。'),('5 最初の案件を選ぶ','利用前に対象条件・費用・期限を保存します。ポイント目的で不要な契約を増やさず、必要なサービスから始めましょう。')]),
'safety':('モッピーの安全性を、確認してから。','運営会社の情報と、案件ごとの費用・条件を分けて確認しましょう。',[
('運営会社は株式会社セレス','モッピー公式の会社概要には、株式会社セレスが運営会社として記載されています。会社情報は下の公式リンクで確認できます。'),('「運営会社がある」だけで判断しない','ポイントの承認や収益を保証するものではありません。広告主との契約内容、継続料金、解約条件、個人情報の取り扱いを確認しましょう。'),('偽サイトを避ける','登録前にアクセス先のドメインを確認してください。POI DAYSは非公式の紹介サイトで、モッピーのログインフォームや本人確認画面は設置していません。'),('反映されない場合','通帳と反映目安を確認し、広告ごとの調査受付期間・必要書類に従ってモッピーへ問い合わせます。広告主へポイントに関する問い合わせを行う前に、公式条件を確認してください。')]),
'categories':('初心者向け・カテゴリ別の案件選び','還元額だけでなく、必要な時間・費用・自分が対象かをそろえて比べましょう。',[
('ゲーム案件','対象OS、初回インストール条件、到達レベル、期限、課金条件を確認します。最終段階だけに高いポイントが割り当てられている場合もあります。現在のゲーム個別案件は未確認のため、数値付きのおすすめは掲載していません。'),('無料案件・無料体験','登録無料と継続無料を区別しましょう。無料体験は終了日と次の請求日を記録。U-NEXTのガイドでは有料作品と自動継続の注意点を確認できます。'),('高還元のショッピング','買う予定の商品だけを対象に、送料と対象外金額まで確認。還元率が高くても購入総額が上がれば節約にならないことがあります。'),('高額案件','カード・電気切替・口座開設などは、もともと必要な人向けです。審査、使用量、継続費用、対象者の条件が違うので、ポイント額の順だけで選ばないでください。'),('初心者に向く選び方','普段使うサービスで、費用と期限を説明できる案件をひとつ選びます。実測していない難易度や達成日数を、簡単・最短と断定しません。')]),
'policy':('運営情報・編集方針','POI DAYSはモッピーの登録方法と案件の進め方を整理する、非公式の紹介サイトです。',[
('広告・PRについて','掲載の招待リンクからの登録・利用で、サイト運営者に紹介報酬が発生する場合があります。モッピー公式の運営会社と当サイトの運営者は異なります。'),('情報の確認とランキング','案件には確認日と公式情報源を掲載します。公式順位と当サイトの選定を区別し、体験していない案件を体験談として紹介しません。古い記録を今日の最新情報とは表示しません。'),('免責事項','掲載内容は確認時点の案内です。申込時点の公式条件をご確認ください。成果承認や利益を保証するものではなく、最終的な利用判断は条件をご確認のうえ行ってください。'),('運営者・お問い合わせ','運営名：POI DAYS。記事の訂正を受け付ける公開連絡先は現在準備中です。ポイント判定やモッピーのアカウントに関する質問は、モッピー公式サポートをご利用ください。')]),
'privacy':('プライバシーポリシー','このサイト内での情報の扱いを説明します。',[
('診断・試算・チェックリスト','入力内容はブラウザ内の表示と計算に使用します。当サイトのコードから送信・保存せず、ページを閉じると失われます。'),('解析と問い合わせ','独自のアクセス解析、広告配信タグ、問い合わせフォームは設置していません。パスワードや認証コードを当サイトへ入力する必要はありません。'),('外部リンクとホスティング','外部サイトでは各サービスの規約・プライバシーポリシーが適用されます。サイト配信事業者がアクセス時の技術情報を取り扱う場合があります。'),('変更について','機能や情報の取り扱いを変更する場合は本ページを更新します。最終更新：2026年9月6日。')])}
footer='<footer><div class="container"><a class="logo" href="/index.html">P<span class="point-o">O</span>I DAYS</a><p>暮らしに合うポイ活を、一つずつ。非公式の情報サイト・PR</p><nav class="footer-links" aria-label="フッター"><a href="/articles/about.html">モッピーとは</a><a href="/articles/registration.html">登録方法</a><a href="/articles/safety.html">安全性</a><a href="/articles/policy.html">運営情報・お問い合わせ</a><a href="/articles/privacy.html">プライバシー</a></nav><small>© 2026 POI DAYS</small></div></footer>'
header='<header class="header"><a class="logo" href="/index.html">P<span class="point-o">O</span>I DAYS</a><nav><a href="/index.html#ranking">案件ランキング</a><a href="/index.html#articles">攻略記事</a></nav><a class="small-button" href="'+e(invite)+'" target="_blank" rel="sponsored noopener">無料ではじめる</a></header>'
(d/'articles').mkdir(exist_ok=True)
for slug,(title,lead,sections) in articles.items():
 body=''.join(f'<section id="part-{i}"><h2>{e(t)}</h2><p>{e(p)}</p></section>' for i,(t,p) in enumerate(sections))
 links='<div class="related-guides">'+''.join(f'<a href="{s}.html">{e(v[0])} →</a>' for s,v in articles.items() if s!=slug)+'</div>'
 sources='<p class="source">参考：<a href="https://pc.moppy.jp/guide/" target="_blank" rel="noopener">モッピー公式ガイド</a> · <a href="https://pc.moppy.jp/st/info/corporate/" target="_blank" rel="noopener">公式会社概要</a></p>'
 (d/'articles'/f'{slug}.html').write_text(f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}｜POI DAYS</title><meta name="description" content="{e(lead)}"><link rel="stylesheet" href="/style.css"></head><body>{header}<main class="guide-main container narrow"><p class="breadcrumb"><a href="/index.html">ホーム</a> / {e(title)}</p><p class="eyebrow">POI DAYS GUIDE · PR</p><h1>{e(title)}</h1><div class="guide-summary"><p>{e(lead)}</p><p class="source">記事更新日：2026年9月6日</p></div>{body}{sources}<section>{cta}</section><section><h2>あわせて読みたい</h2>{links}<p><a href="/index.html#articles">案件の攻略記事一覧 →</a></p></section></main>{footer}</body></html>')
# Enrich shared offer schema without inventing performance data.
offers=json.loads((root/'content/offers.json').read_text())
for o in offers:
 o.update(checkedAt='2026-09-05',os='公式の対応端末・ブラウザ条件を確認',difficulty='未評価（実測データなし）',recommendation='条件が合う人向け',duration='達成日数は未確認。条件の期限と付与時期は別です。')
(root/'content/offers.json').write_text(json.dumps(offers,ensure_ascii=False,indent=2)+'\n')
for o in offers:
 p=d/'guides'/f'{o["id"]}.html';s=p.read_text();currency=f'{o["points"]:,}円相当' if o['points'] else '対象金額1,000円なら10P＝10円相当（計算例）'
 extra='<section><h2>自分に合うか、比べよう。</h2><dl class="condition-table">'+''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k,v in [('円換算',currency),('対象OS',o['os']),('達成目安',o['duration']),('難易度',o['difficulty']),('おすすめ度',o['recommendation']),('おすすめ理由',o['fit'])])+'</dl></section>'
 tips=f'<section><h2>進めるコツと、途中の確認。</h2><div class="guide-summary"><p>{e(o["pitfalls"][0])}</p></div><ol class="guide-steps"><li><span>開始時</span><p>対象条件と開始日時を保存し、期限をカレンダーに記録。</p></li><li><span>手続き後</span><p>完了メール・受付番号を保管。予定反映の目安：{e(o["pending"])}。</p></li><li><span>条件達成後</span><p>達成した証拠を保管し通帳を確認。確定反映の目安：{e(o["confirmed"])}。</p></li></ol><p class="micro">これは確認の順番です。実測の日別攻略や達成保証ではありません。</p></section><section>{cta}</section>'
 s=s.replace('<section id="howto">',extra+'<section id="howto">').replace('<section id="questions">',tips+'<section id="questions">');s=re.sub(r'<footer>.*?</footer>',footer,s,flags=re.S);p.write_text(s)
p=d/'index.html';s=p.read_text()
# Place background understanding before offers, preserving original section styling.
m=re.search(r'<!-- OFFERS START -->.*?<!-- OFFERS END -->',s,re.S);block=m.group();s=s.replace(block,'');s=s.replace('<section class="section" id="diagnosis">',block+'<section class="section" id="diagnosis">') if '<section class="section" id="diagnosis">' in s else s.replace('<section id="diagnosis"',block+'<section id="diagnosis"')
if block not in s:s=s.replace('<section class="section campaign"',block+'<section class="section campaign"',1)
intro='<section class="section learning"><div class="container"><p class="eyebrow">YOUR FIRST STEP</p><h2>知ってから、安心して始めよう。</h2><div class="offer-grid">'+''.join(f'<article class="offer-card"><p class="eyebrow">GUIDE 0{i}</p><h3>{e(articles[k][0])}</h3><p>{e(articles[k][1])}</p><a class="text-link" href="articles/{k}.html">詳しく読む →</a></article>' for i,k in enumerate(['about','registration','safety'],1))+'</div></div></section>'
s=s.replace('<!-- OFFERS START -->',intro+'<!-- OFFERS START -->',1)
cards=''.join(f'<a class="article-link" href="guides/{o["id"]}.html"><span>{e(o["category"])}</span><h3>{e(o["name"])}</h3><p>獲得条件・やり方・失敗しやすいポイント →</p></a>' for o in offers)
section='<section class="section article-hub" id="articles"><div class="container"><p class="eyebrow">READ & TRY</p><h2>あなたに合う、次の一歩。</h2><p class="section-lead">ゲーム・無料体験・高還元・高額案件。<br>費用と条件から選びましょう。</p><a class="button outline" href="articles/categories.html">カテゴリ別の選び方を見る →</a><h2 class="more-guides-heading">攻略記事一覧</h2><div class="article-grid">'+cards+'</div><div class="update-card"><p class="eyebrow">UPDATES</p><h3>2026年9月6日 更新</h3><p>5件の案件手順と、登録・安全性・カテゴリ別ガイドを追加しました。案件の金額・順位は9月5日の確認記録です。</p></div></div></section>'
s=s.replace('<section class="final-cta">',section+'<section class="final-cta">');s=re.sub(r'<footer>.*?</footer>',footer,s,flags=re.S)
s=s.replace('このページでは、個別案件の最新還元額の比較は掲載していません。','案件ガイドに確認日付きの条件を掲載しています。申込直前には公式情報を確認してください。')
s=s.replace('<p class="micro">登録不要・無料で診断できます</p>','<p class="micro">登録不要・無料で診断できます</p><a class="text-link invite-link" href="'+e(invite)+'" target="_blank" rel="sponsored noopener">モッピーを無料で始める →</a>')
p.write_text(s)
base='https://poi-days.lolipopsaya.chatgpt.site'
for p in d.rglob('*.html'):
 s=p.read_text();url=base+'/'+p.relative_to(d).as_posix();s=s.replace('</head>',f'<link rel="canonical" href="{url}"></head>');p.write_text(s)
(d/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+base+'/'+p.relative_to(d).as_posix()+'</loc></url>' for p in sorted(d.rglob('*.html')))+'</urlset>')
(d/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'/sitemap.xml\n')
from enrich import enrich
enrich(root)
from visuals import apply_visuals
apply_visuals(root)
