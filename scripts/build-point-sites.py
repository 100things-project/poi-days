"""Generate factual point-site profile pages from reviewed official-source data."""
from pathlib import Path
from html import escape as e
import json, os

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/point-sites.json').read_text(encoding='utf-8'))
BASE=os.environ.get('SITE_URL','https://100things-project.github.io/poi-days').rstrip('/')
CHECKED=DATA['checkedAt']

CSS='''<style>
:root{--green:#006653;--ink:#17302d;--muted:#64706b;--line:#e6ebe6;--cream:#fcfaf4;--mint:#e8f3ed;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;color:var(--ink);background:#f4f5f1}*{box-sizing:border-box}body{margin:0;line-height:1.8;background:#f4f5f1}a{color:inherit}.shell{max-width:680px;margin:auto;background:#fff;min-height:100vh}.head{padding:18px;border-bottom:1px solid var(--line)}.brand{font-weight:850;letter-spacing:.06em;color:var(--green);text-decoration:none;font-size:24px}.hero{padding:34px 20px;background:var(--cream)}.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--green);font-weight:700}.hero h1{font-size:30px;line-height:1.4;margin:6px 0 12px}.hero p{margin:0}.section{padding:28px 20px;border-bottom:1px solid var(--line)}.section h2{font-size:20px;margin:0 0 14px}.facts{display:grid;gap:0;padding:0;margin:0;list-style:none;border-top:1px solid var(--line)}.facts li{padding:13px 0;border-bottom:1px solid var(--line);font-size:15px}.fit{background:var(--mint);border-radius:10px;padding:16px}.actions{display:grid;gap:10px;margin-top:18px}.button{display:flex;justify-content:center;align-items:center;min-height:48px;border-radius:24px;padding:9px 16px;text-decoration:none;font-weight:700}.primary{background:var(--green);color:#fff}.secondary{background:#eef3ef;color:var(--green)}.note{font-size:12px;color:var(--muted)}.footer{padding:28px 20px;background:#edf3ee;font-size:12px;color:var(--muted)}@media(min-width:430px){.hero,.section{padding-left:28px;padding-right:28px}}
</style>'''

def write(path,text):
 for folder in ('docs','dist'):
  p=ROOT/folder/path
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(text,encoding='utf-8')

def page(site):
 name=site['name']
 facts=''.join(f'<li>{e(x)}</li>' for x in site['facts'])
 register_rel=e(site.get('registerRel') or 'noopener',quote=True)
 description=e(site['summary'],quote=True)
 canonical=f'{BASE}/{site["page"]}'
 return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#006653"><title>{e(name)}とは？特徴と公式情報｜POI DAYS</title><meta name="description" content="{description}"><link rel="canonical" href="{e(canonical,quote=True)}"><script src="analytics.js" defer></script>{CSS}</head><body><div class="shell"><header class="head"><a class="brand" href="index.html">POI DAYS</a></header><main><section class="hero"><p class="eyebrow">POINT SITE GUIDE</p><h1>{e(name)}とは？</h1><p>{e(site['summary'])}</p></section><section class="section"><h2>公式情報で確認できた特徴</h2><ul class="facts">{facts}</ul><p class="note">確認日：{e(CHECKED)}。数値や制度は変更される場合があるため、登録・利用前に公式ページをご確認ください。</p></section><section class="section"><h2>こんな人に向きそう</h2><div class="fit">{e(site['bestFor'])}</div><p class="note">POI DAYSによる整理であり、公式の推薦表現ではありません。</p></section><section class="section"><h2>公式ページで確認する</h2><p>登録条件、開催中のキャンペーン、交換条件などの最新情報は公式ページが優先です。</p><div class="actions"><a class="button primary" href="{e(site['registerUrl'],quote=True)}" target="_blank" rel="{register_rel}">{e(name)}の公式登録・案内を見る →</a><a class="button secondary" href="{e(site['sourceUrl'],quote=True)}" target="_blank" rel="noopener">出典：{e(site['sourceLabel'])} →</a><a class="button secondary" href="index.html#ranking">今日のランキングを見る →</a></div></section></main><footer class="footer">POI DAYSは非公式の情報メディアです。モッピーの紹介リンク経由では運営者が紹介報酬を受け取る場合があります。その他の掲載先は現時点では公式ページへの案内です。</footer></div></body></html>'''

def main():
 generated=[]
 for site in DATA['sites']:
  # The existing Moppy page is already a richer dedicated page and must not be replaced.
  if site['id']=='moppy':
   continue
  write(site['page'],page(site));generated.append(site['page'])
 print('Point-site profiles built:',', '.join(generated))

if __name__=='__main__':main()
