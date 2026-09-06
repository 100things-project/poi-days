"""Original, informational SVG diagrams; no third-party logos or artwork."""
from html import escape
import re

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
 flow='''<figure class="visual-flow"><figcaption>ポイント獲得までの4ステップ</figcaption><ol><li><span>01</span><strong>公式で登録</strong><small>紹介条件を確認</small></li><li><span>02</span><strong>広告を経由</strong><small>利用前に条件を保存</small></li><li><span>03</span><strong>条件を達成</strong><small>期限・費用を確認</small></li><li><span>04</span><strong>承認・獲得</strong><small>通帳を見て交換へ</small></li></ol><p>予定反映は獲得確定ではありません。</p></figure>'''
 for p in d.rglob('*.html'):
  s=p.read_text()
  if p.name=='index.html':
   # Each ranking tile gets a process thumbnail, not an advertisement/logo.
   def card(m):
    chunk=m[0];match=re.search(r'guides/([a-z-]+)\.html',chunk)
    if match and match[1] in VISUALS:return chunk.replace('>', '>'+thumb(match[1]),1)
    return chunk
   s=re.sub(r'<article class="offer-card">.*?</article>',card,s,flags=re.S)
   s=s.replace('<h2>登録後の流れ</h2>','<h2>登録後の流れ</h2>'+flow,1)
  elif p.stem in ['about','registration']:
   s=s.replace('<section id="part-0">',flow+'<section id="part-0">',1)
  elif p.stem in VISUALS and p.parent.name=='guides':
   s=s.replace('<nav class="guide-toc"',thumb(p.stem,'guide-process')+'<nav class="guide-toc"',1)
  # Article list and related tiles: identify the destination, keep labels accessible.
  def article(m):
   chunk=m[0];url=re.search(r'href="([^"]+)"',chunk)
   if not url:return chunk
   key=url[1].split('/')[-1].split('.html')[0]
   if key in VISUALS:return chunk.replace('>', '>'+thumb(key),1)
   return chunk
  s=re.sub(r'<a class="(?:article-link|journey-tile)"[^>]*>.*?</a>',article,s,flags=re.S)
  # Purpose entries with fragment-only URLs have compact semantic category markers.
  for text,symbol in [('無料から検討したい','¥0'),('ゲームを楽しみたい','▶'),('還元を活かしたい','%'),('何から始めるか迷う','?')]:
   s=s.replace('<h3>'+text+'</h3>','<span class="category-symbol" aria-hidden="true">'+symbol+'</span><h3>'+text+'</h3>')
  s=s.replace('</head>','<link rel="stylesheet" href="/visuals.css"></head>')
  p.write_text(s)
