"""Add measured invite CTAs to selected high-intent Moppy articles."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INVITE = "https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1"

TOP_CTA = {
    "moppy-registration.html": (
        "article_top_registration",
        "登録する前に、紹介条件を確認",
        "現在の対象条件・期限を公式ページで確認してから登録へ進めます。",
        "紹介条件を確認して無料登録へ →",
    ),
    "moppy-earning.html": (
        "article_top_earning",
        "始め方が決まったら、登録条件を確認",
        "無料登録の前に、紹介特典の対象条件と期限を公式ページで確認できます。",
        "紹介条件を確認して無料登録へ →",
    ),
}


def insert_after_first_key(text: str, location: str, title: str, copy: str, label: str) -> str:
    marker = 'data-poidays-top-cta="true"'
    if marker in text:
        return text
    block = (
        f'<div class="seo-note" {marker}><strong>{title}</strong><p>{copy}</p>'
        f'<p><a class="button primary" data-cta-location="{location}" href="{INVITE.replace("&", "&amp;")}" '
        f'target="_blank" rel="sponsored noopener">{label}</a></p>'
        '<p class="seo-example">PR・紹介リンク。登録・利用によりPOI DAYS運営者が紹介報酬を受け取る場合があります。</p></div>'
    )
    new, count = re.subn(r'(<div class="seo-key">.*?</div>)', r'\1\n' + block, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("top CTA insertion point not found")
    return new


def tag_referral_cta(text: str) -> str:
    if 'data-cta-location="article_top_referral"' in text:
        return text
    old = '<a class="button primary" href="https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&amp;openExternalBrowser=1"'
    new = '<a class="button primary" data-cta-location="article_top_referral" href="https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&amp;openExternalBrowser=1"'
    if old not in text:
        raise RuntimeError("referral top CTA not found")
    return text.replace(old, new, 1)


def tag_registration_steps_cta(text: str) -> str:
    if 'data-cta-location="article_steps_registration"' in text:
        return text
    old = '<a class="button primary" href="https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&amp;openExternalBrowser=1"'
    new = '<a class="button primary" data-cta-location="article_steps_registration" href="https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&amp;openExternalBrowser=1"'
    if old not in text:
        raise RuntimeError("registration steps CTA not found")
    return text.replace(old, new, 1)


for folder in (ROOT / "docs" / "articles", ROOT / "dist" / "articles"):
    for name, args in TOP_CTA.items():
        path = folder / name
        text = insert_after_first_key(path.read_text(encoding="utf-8"), *args)
        if name == "moppy-registration.html":
            text = tag_registration_steps_cta(text)
        path.write_text(text, encoding="utf-8")

    referral = folder / "moppy-referral-code.html"
    referral.write_text(tag_referral_cta(referral.read_text(encoding="utf-8")), encoding="utf-8")

for folder in (ROOT / "docs" / "articles", ROOT / "dist" / "articles"):
    for name, (location, *_rest) in TOP_CTA.items():
        text = (folder / name).read_text(encoding="utf-8")
        assert text.count('data-poidays-top-cta="true"') == 1
        assert text.count(f'data-cta-location="{location}"') == 1
    registration = (folder / "moppy-registration.html").read_text(encoding="utf-8")
    assert registration.count('data-cta-location="article_steps_registration"') == 1
    referral = (folder / "moppy-referral-code.html").read_text(encoding="utf-8")
    assert referral.count('data-cta-location="article_top_referral"') == 1

print("Invite CTA enrichment complete: registration, referral, earning")
