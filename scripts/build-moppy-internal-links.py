"""Strengthen internal links among the eight Moppy search-intent guides."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DOCS,DIST=ROOT/'docs',ROOT/'dist'

ROUTES={
 'moppy-referral-code':[
  ('moppy-september-campaign','2026年9月のキャンペーン条件を確認'),
  ('moppy-registration','モッピーの登録方法を見る'),
  ('moppy-safety','登録前に安全性を確認'),
 ],
 'moppy-september-campaign':[
  ('moppy-referral-code','紹介コードの入力方法を確認'),
  ('moppy-registration','登録手順を確認'),
  ('moppy-pros-cons','メリット・デメリットを見る'),
 ],
 'moppy-registration':[
  ('moppy-referral-code','紹介コードを入れる場所を確認'),
  ('moppy-september-campaign','今月の入会特典を確認'),
  ('moppy-safety','登録前に安全性を確認'),
 ],
 'moppy-safety':[
  ('moppy-pros-cons','メリット・デメリットを確認'),
  ('moppy-reviews','実際の評判・口コミを見る'),
  ('moppy-registration','納得できたら登録方法を確認'),
 ],
 'moppy-reviews':[
  ('moppy-safety','安全性を公式情報で確認'),
  ('moppy-pros-cons','メリット・デメリットを整理'),
  ('moppy-registration','登録方法を見る'),
 ],
 'moppy-pros-cons':[
  ('moppy-safety','安全性と仕組みを確認'),
  ('moppy-reviews','評判・口コミも確認'),
  ('moppy-registration','登録方法を見る'),
 ],
 'moppy-earning':[
  ('moppy-games','ゲーム案件の選び方を見る'),
  ('moppy-pros-cons','メリット・デメリットを確認'),
  ('moppy-registration','始める前に登録方法を確認'),
 ],
 'moppy-games':[
  ('moppy-earning','初心者向けの稼ぎ方を見る'),
  ('moppy-pros-cons','登録前の注意点を確認'),
  ('moppy-registration','ゲーム開始前に登録方法を確認'),
 ],
}

for root in (DOCS,DIST):
 for slug,links in ROUTES.items():
  path=root/'articles'/f'{slug}.html'
  text=path.read_text(encoding='utf-8')
  new='<section class="seo-next"><h2>次に読む</h2>'+''.join(
   f'<a href="{target}.html">{label} →</a>' for target,label in links
  )+'</section>'
  text,count=re.subn(r'<section class="seo-next"><h2>次に読む</h2>.*?</section>',new,text,count=1,flags=re.S)
  if count!=1:
   raise SystemExit(f'seo-next section not found exactly once: {path}')
  path.write_text(text,encoding='utf-8')

print('Moppy internal journey built: 8 guides linked by search intent')
