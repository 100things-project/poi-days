"""Original, informational SVG diagrams; no third-party logos or artwork."""
from html import escape
import re
import shutil

SCENES={
 'game':('ゲームで貯める','好きなアプリを楽しみながら','▶'),
 'shopping':('ショッピングで貯める','いつもの買い物の前に経由','🛒'),
 'service':('サービス申込で貯める','必要な申込をおトクに','▰'),
 'spare':('スキマ時間で貯める','短い時間でコツコツ','◷'),
}

VISUALS={
 'mufg-card':('カード発行',['申込','受取','判定'],'45日以内の受取が条件'),
 'eneone':('電気の切替',['申込','供給','使用量'],'2回目の請求分を確認'),
 'rakuten-bank':('口座開設',['WEB','開設','ログイン'],'初回ログインまでが条件'),
 'unext':('無料体験',['登録','体験','継続判断'],'無料期間の終了日を記録'),
 'rakuten-shopping':('お買い物',['経由','購入','判定'],'購入前にモッピーを経由'),
 'about':('ポイントの仕組み',['広告費','還元','ポイント'],'条件達成と承認が必要'),
 'registration':('登録の準備',['特典確認','公式登録','案件選び'],'会員情報は公式サイトだけで入力'),
 'safety':('安心の確認',['運営元','費用','条件'],'納得してから始めよう'),
 'categories':('自分に合う選び方',['時間','費用','対象条件'],'還元額だけで決めない'),
 'game':('ゲーム案件',['OS','到達条件','期限'],'開始前に条件を保存'),
}

def apply_visuals(root):
 d=root/'dist';assets=d/'visuals';assets.mkdir(exist_ok=True)
 for key in SCENES:
  (assets/f'way-{key}.svg').unlink(missing_ok=True)
  shutil.copy2(root/'content'/'assets'/f'way-{key}.webp',assets/f'way-{key}.webp')
 for key,(title,labels,note) in VISUALS.items():
  nodes=''
  for i,label in enumerate(labels):
   x=85+i*155
   nodes+=f'<circle cx="{x}" cy="96" r="34" fill="white" stroke="#007975" stroke-width="2"/><text x="{x}" y="102" text-anchor="middle" fill="#007975" font-size="16" font-weight="700">{escape(label)}</text>'
   if i<2:nodes+=f'<path d="M{x+44} 96h62m-8-6 8 6-8 6" fill="none" stroke="#ab695c" stroke-width="2"/>'
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 180" width="480" height="180"><rect width="480" height="180" rx="16" fill="#f3f7f2"/><path d="M0 0h480v42H0z" fill="#fff4e3"/><g font-family="sans-serif"><text x="24" y="28" fill="#272b2d" font-size="18" font-weight="700">{escape(title)}</text>{nodes}<text x="240" y="161" text-anchor="middle" fill="#626b76" font-size="14">{escape(note)}</text></g></svg>'
  svg=svg.replace('font-size="16"','font-size="21"').replace('font-size="14"','font-size="20"').replace('font-size="18"','font-size="24"')
  (assets/f'{key}.svg').write_text(svg)
 def thumb(key,cls='info-thumb'):
  title,labels,note=VISUALS[key]
  return f'<img class="{cls}" src="/visuals/{key}.svg" width="480" height="180" loading="lazy" decoding="async" alt="{escape(title)}：'+escape(' → '.join(labels)+'。'+note)+'">'
 # Real text, not an image of a login screen; stacks at mobile widths.
 flow='''<figure class="visual-flow"><figcaption><span>かんたん4ステップ</span>ポイント獲得までの流れ</figcaption><ol><li><span>01</span><i aria-hidden="true">✓</i><strong>無料会員登録</strong><small>紹介条件を確認</small></li><li><span>02</span><i aria-hidden="true">⌕</i><strong>案件を選ぶ</strong><small>費用・期限を保存</small></li><li><span>03</span><i aria-hidden="true">▤</i><strong>条件を達成</strong><small>公式手順どおりに進む</small></li><li><span>04</span><i aria-hidden="true">P</i><strong>ポイントGET</strong><small>承認後に交換へ</small></li></ol><p>予定反映は獲得確定ではありません。案件ごとの条件を優先してください。</p></figure>'''
 for p in d.rglob('*.html'):
  s=p.read_text()
  if p.name=='index.html':
   # Each ranking tile gets a process thumbnail, not an advertisement/logo.
   def card(m):
    chunk=m[0];match=re.search(r'guides/([a-z-]+)\.html',chunk)
    if match and match[1] in VISUALS:return chunk.replace('>', '>'+thumb(match[1]),1)
    return chunk
   s=re.sub(r'<article class="offer-card">.*?</article>',card,s,flags=re.S)
   # One registration flow: replace the older three cards, then keep the
   # practical checklist and expandable details that follow.
   s=s.replace('<h2>登録後の流れ</h2>','<h2>はじめてなら、この順番で。</h2>',1)
   s=re.sub(r'<p class="section-lead">まずは、ひとつの案件から。</p><ol class="steps">.*?</ol>',flow,s,count=1,flags=re.S)
   exchange='''<figure class="exchange-map"><figcaption>貯めたポイントの交換先</figcaption><div class="exchange-line" aria-label="貯めたポイントを現金、電子マネー、ギフト券、マイルなどへ交換"><div class="exchange-source"><strong>P</strong><span>ポイント</span></div><span class="exchange-arrow" aria-hidden="true">→</span><ul><li><b>現金</b><small>銀行振込など</small></li><li><b>電子マネー</b><small>日常のお支払いに</small></li><li><b>ギフト券</b><small>お買い物に</small></li><li><b>マイル</b><small>旅行の楽しみに</small></li></ul></div></figure>'''
   s=s.replace('<div class="exchange-tags"><span>現金</span><span>電子マネー</span><span>ギフト券</span><span>マイル</span></div>',exchange,1)
   for old,new in [
    ('<span class="reason-symbol" aria-hidden="true">◎</span>','<span class="reason-symbol reason-people" aria-hidden="true"><i></i><i></i><i></i></span>'),
    ('<span class="reason-symbol" aria-hidden="true">◇</span>','<span class="reason-symbol reason-calendar" aria-hidden="true"><b>20</b></span>'),
    ('<span class="reason-symbol" aria-hidden="true">P</span>','<span class="reason-symbol reason-coin" aria-hidden="true">P</span>'),
    ('<span class="reason-symbol" aria-hidden="true">↔</span>','<span class="reason-symbol reason-gift" aria-hidden="true">◇</span>')]:
    s=s.replace(old,new,1)
  elif p.stem in ['about','registration']:
   s=s.replace('<section id="part-0">',flow+'<section id="part-0">',1)
  elif p.stem in VISUALS and p.parent.name=='guides':
   s=s.replace('<nav class="guide-toc"',thumb(p.stem,'guide-process')+'<nav class="guide-toc"',1)
  # Article list and related tiles: identify the destination, keep labels accessible.
  def article(m):
   chunk=m[0];url=re.search(r'href="([^"]+)"',chunk)
   if 'purpose-photo' in chunk:return chunk
   if not url:return chunk
   key=url[1].split('/')[-1].split('.html')[0]
   if key in VISUALS:return chunk.replace('>', '>'+thumb(key),1)
   return chunk
  s=re.sub(r'<a class="(?:article-link|journey-tile)"[^>]*>.*?</a>',article,s,flags=re.S)
  visual_version='20260906-6' if p.name=='index.html' else '20260906-6' if p.stem=='about' else '20260906-2'
  s=s.replace('</head>',f'<link rel="stylesheet" href="/visuals.css?v={visual_version}"></head>')
  p.write_text(s)
