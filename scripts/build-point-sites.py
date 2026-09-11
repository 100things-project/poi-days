"""Generate factual point-site profile pages from reviewed official-source data."""
from pathlib import Path
from html import escape as e
import json, os

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/point-sites.json').read_text(encoding='utf-8'))
BASE=os.environ.get('SITE_URL','https://100things-project.github.io/poi-days').rstrip('/')
CHECKED=DATA['checkedAt']

CSS='''<style>
:root{--green:#006653;--ink:#17302d;--muted:#64706b;--line:#e6ebe6;--cream:#fcfaf4;--mint:#e8f3ed;--orange:#d97822;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;color:var(--ink);background:#f4f5f1}*{box-sizing:border-box}body{margin:0;line-height:1.8;background:#f4f5f1}a{color:inherit}.shell{max-width:720px;margin:auto;background:#fff;min-height:100vh}.head{padding:18px 20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.brand{display:inline-flex;align-items:center;min-height:44px;font-weight:850;letter-spacing:.06em;color:var(--green);text-decoration:none;font-size:24px}.home{font-size:13px;color:var(--green);text-decoration:none}.hero{padding:38px 20px 34px;background:linear-gradient(180deg,#fff9ed 0%,var(--cream) 100%)}.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--green);font-weight:700}.hero h1{font-size:32px;line-height:1.35;margin:7px 0 12px}.hero p{margin:0;word-break:auto-phrase;text-wrap:pretty}.hero .cta{margin-top:22px}.section{padding:30px 20px;border-bottom:1px solid var(--line)}.section h2{font-size:21px;margin:0 0 14px}.section h3{font-size:16px;margin:20px 0 6px}.facts{display:grid;gap:0;padding:0;margin:0;list-style:none;border-top:1px solid var(--line)}.facts li{padding:13px 0;border-bottom:1px solid var(--line);font-size:15px}.fit,.invite,.mini{word-break:auto-phrase;text-wrap:pretty}.fit{background:var(--mint);border-radius:10px;padding:16px}.steps{margin:0;padding-left:1.4em}.steps li{margin:8px 0}.invite{border:1px solid #f0d9bd;background:#fffaf1;border-radius:14px;padding:18px;margin-top:14px}.invite strong{display:block;font-size:13px;color:#6e512d}.invite-code{font-size:28px;font-weight:850;letter-spacing:.08em;color:var(--orange);margin:3px 0 10px}.actions{display:grid;gap:10px;margin-top:18px}.button{display:flex;justify-content:center;align-items:center;min-height:50px;border-radius:25px;padding:10px 16px;text-decoration:none;font-weight:800;text-align:center;text-wrap:balance}.primary{background:var(--green);color:#fff}.secondary{background:#eef3ef;color:var(--green)}.note{font-size:12px;color:var(--muted);word-break:auto-phrase;text-wrap:pretty}.mini{font-size:14px}.footer{padding:28px 20px;background:#edf3ee;font-size:12px;color:var(--muted);word-break:auto-phrase;text-wrap:pretty}@media(min-width:430px){.hero,.section{padding-left:30px;padding-right:30px}}
</style>'''

def write(path,text):
 for folder in ('docs','dist'):
  p=ROOT/folder/path
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(text,encoding='utf-8')

def common_head(site):
 name=site['name']; description=e(site['summary'],quote=True); canonical=f'{BASE}/{site["page"]}'
 return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#006653"><title>{e(name)}とは？特徴・登録方法・紹介コード｜POI DAYS</title><meta name="description" content="{description}"><link rel="canonical" href="{e(canonical,quote=True)}"><script src="analytics.js" defer></script>{CSS}</head>'''

def hapitas_page(site):
 facts=''.join(f'<li>{e(x)}</li>' for x in site['facts'])
 rel=e(site.get('registerRel') or 'noopener',quote=True)
 code=e(site.get('inviteCode',''))
 reg=e(site['registerUrl'],quote=True)
 src=e(site['sourceUrl'],quote=True)
 return common_head(site)+f'''<body><div class="shell"><header class="head"><a class="brand" href="index.html">POI DAYS</a><a class="home" href="index.html">トップへ</a></header><main>
<section class="hero"><p class="eyebrow">POINT SITE GUIDE</p><h1>ハピタスとは？</h1><p>{e(site['summary'])}</p><div class="cta"><a class="button primary" href="{reg}" target="_blank" rel="{rel}">紹介リンクからハピタスを始める →</a></div><p class="note">このリンクは紹介リンクです。登録・利用によりPOI DAYS運営者が紹介報酬を受け取る場合があります。</p></section>
<section class="section"><h2>ハピタスの特徴</h2><ul class="facts">{facts}</ul><p class="note">確認日：{e(CHECKED)}。数値や制度は変更される場合があるため、登録・利用前に公式ページをご確認ください。</p></section>
<section class="section"><h2>こんな人に向きそう</h2><div class="fit">{e(site['bestFor'])}</div><p class="note">POI DAYSによる整理であり、公式の推薦表現ではありません。</p></section>
<section class="section"><h2>ハピタスの基本的な使い方</h2><ol class="steps"><li>ハピタスに登録する</li><li>買い物や申込み前にハピタスを経由する</li><li>案件の条件を確認して利用する</li><li>判定期間を経てポイントが反映されたら交換する</li></ol><p class="note">案件ごとに獲得条件・対象外条件・判定期間が異なります。利用前に必ず案件詳細をご確認ください。</p></section>
<section class="section"><h2>紹介リンク・紹介コード</h2><p class="mini">POI DAYSから登録する場合は、下の紹介リンクまたは紹介コードをご利用いただけます。</p><div class="invite"><strong>紹介コード</strong><div class="invite-code">{code}</div><p class="note">コードの入力欄や適用条件は、登録画面の案内を優先してください。</p></div><div class="actions"><a class="button primary" href="{reg}" target="_blank" rel="{rel}">紹介リンクから登録する →</a><a class="button secondary" href="{src}" target="_blank" rel="noopener">ハピタス公式情報を確認する →</a></div></section>
<section class="section"><h2>登録前に確認したいこと</h2><p class="mini">ポイントサイトは、案件ごとに条件が細かく決まっています。「広告を利用しただけ」で必ずポイントが付くとは限りません。</p><ul class="facts"><li>獲得条件・対象外条件を読む</li><li>申込み前にCookieやブラウザ設定を確認する</li><li>申込み完了画面や条件を必要に応じて保存する</li><li>高還元でも、自分が達成できる条件か確認する</li></ul><div class="actions"><a class="button secondary" href="articles/point-site-selection.html">ポイントサイトの選び方を見る →</a><a class="button secondary" href="index.html#ranking">今日のハピタスランキングを見る →</a></div></section>
</main><footer class="footer">POI DAYSは非公式の情報メディアです。このページにはハピタスの紹介リンクを含み、登録・利用により運営者が紹介報酬を受け取る場合があります。最新の条件・キャンペーンはハピタス公式ページをご確認ください。</footer></div></body></html>'''

def simple_page(site):
 name=site['name']; facts=''.join(f'<li>{e(x)}</li>' for x in site['facts']); rel=e(site.get('registerRel') or 'noopener',quote=True)
 return common_head(site)+f'''<body><div class="shell"><header class="head"><a class="brand" href="index.html">POI DAYS</a><a class="home" href="index.html">トップへ</a></header><main><section class="hero"><p class="eyebrow">POINT SITE GUIDE</p><h1>{e(name)}とは？</h1><p>{e(site['summary'])}</p></section><section class="section"><h2>公式情報で確認できた特徴</h2><ul class="facts">{facts}</ul><p class="note">確認日：{e(CHECKED)}。数値や制度は変更される場合があるため、登録・利用前に公式ページをご確認ください。</p></section><section class="section"><h2>こんな人に向きそう</h2><div class="fit">{e(site['bestFor'])}</div><p class="note">POI DAYSによる整理であり、公式の推薦表現ではありません。</p></section><section class="section"><h2>公式ページで確認する</h2><p>登録条件、開催中のキャンペーン、交換条件などの最新情報は公式ページが優先です。</p><div class="actions"><a class="button primary" href="{e(site['registerUrl'],quote=True)}" target="_blank" rel="{rel}">{e(name)}の公式登録・案内を見る →</a><a class="button secondary" href="{e(site['sourceUrl'],quote=True)}" target="_blank" rel="noopener">出典：{e(site['sourceLabel'])} →</a><a class="button secondary" href="index.html#ranking">今日のランキングを見る →</a></div></section></main><footer class="footer">POI DAYSは非公式の情報メディアです。紹介リンクを含むページでは、登録・利用により運営者が紹介報酬を受け取る場合があります。</footer></div></body></html>'''

def page(site):
 return hapitas_page(site) if site['id']=='hapitas' else simple_page(site)

def main():
 generated=[]
 for site in DATA['sites']:
  if site['id']=='moppy':
   continue
  write(site['page'],page(site));generated.append(site['page'])
 print('Point-site profiles built:',', '.join(generated))

if __name__=='__main__':main()