"""Inject a durable Moppy article-navigation section into the public hub page."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
TARGETS=[ROOT/'docs'/'moppy.html', ROOT/'dist'/'moppy.html']
START='<!-- MOPPY ARTICLE NAV START -->'
END='<!-- MOPPY ARTICLE NAV END -->'

SECTION='''<!-- MOPPY ARTICLE NAV START -->
<section class="section moppy-reading" id="moppy-reading"><div class="container">
<p class="eyebrow">READ BEFORE YOU JOIN</p><h2>登録前に、気になるところだけ読めます。</h2>
<p class="section-lead">紹介コード、今月の特典、安全性、評判、登録方法。知りたい順にどうぞ。</p>
<div style="max-width:920px;margin:24px auto 0;border-top:1px solid #e7e2dc">
<a href="articles/moppy-referral-code.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>2026年9月の紹介コード</strong><br><small>入力場所・後付け・特典を確認</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-september-campaign.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>2026年9月の新規登録キャンペーン</strong><br><small>30P・2,000P・5,000Pの対象を整理</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-registration.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>モッピーの登録方法</strong><br><small>紹介リンクと招待コードの使い方</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-safety.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>モッピーは怪しい？安全性を確認</strong><br><small>仕組み・運営・注意点を公式情報で見る</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-reviews.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>モッピーの評判・口コミ</strong><br><small>良い声と悪い声を分けて確認</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-pros-cons.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>メリット・デメリット</strong><br><small>登録前に向いている人を確認</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-earning.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>初心者向けの稼ぎ方</strong><br><small>最初に何から始めるかを整理</small></span><span aria-hidden="true">→</span></a>
<a href="articles/moppy-games.html" style="display:flex;gap:16px;justify-content:space-between;align-items:center;padding:18px 4px;border-bottom:1px solid #e7e2dc;text-decoration:none"><span><strong>ゲーム案件の選び方</strong><br><small>期限・OS・課金条件の見方</small></span><span aria-hidden="true">→</span></a>
</div>
<p style="margin-top:18px"><a class="text-link" href="articles/index.html">モッピー記事を一覧で見る →</a></p>
</div></section>
<!-- MOPPY ARTICLE NAV END -->'''

for path in TARGETS:
    text=path.read_text(encoding='utf-8')
    text=re.sub(re.escape(START)+r'.*?'+re.escape(END), '', text, flags=re.S)
    anchor='<section class="section ranking" id="ranking">'
    if anchor not in text:
        raise SystemExit(f'Moppy ranking anchor not found in {path}')
    text=text.replace(anchor, SECTION+anchor, 1)
    path.write_text(text,encoding='utf-8')
print('Moppy hub navigation built: 8 article routes linked before ranking')
