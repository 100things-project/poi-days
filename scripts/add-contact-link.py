"""Add the Google Form contact link to every public page footer (and the home menu).

Idempotent: safe to run on every build. Writes both docs/ and dist/ so they stay identical.
Uses only relative page links elsewhere; the form is an absolute external URL, so the
/poi-days/ subpath cannot break it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORM = ('https://docs.google.com/forms/d/e/1FAIpQLSfjHaGmX0Q-55saiNXmHix0oNMi0XKCYxeXk4YoyGkck94vkQ/viewform')
LINK = f'<a href="{FORM}" target="_blank" rel="noopener noreferrer">'
MARK = '<!-- POIDAYS:contact -->'
STYLE = ('<style>.poidays-contact{margin:16px auto 0;padding:12px 16px;max-width:520px;box-sizing:border-box;'
         'background:#fffaf0;border:1px solid #f1d2b0;border-radius:10px;text-align:center;'
         'font-size:14px;line-height:1.7;color:#17302d}.poidays-contact p{margin:0 0 4px;color:#17302d}'
         '.poidays-contact a{display:inline-block;padding:8px 18px;border-radius:999px;background:#d97822;'
         'color:#fff;font-weight:700;text-decoration:none}.poidays-contact a:focus-visible{outline:3px solid #006653;outline-offset:2px}</style>')
BLOCK = (f'{MARK}{STYLE}<div class="poidays-contact"><p>ご質問・ご感想・情報提供はこちら</p>'
         f'{LINK}お問い合わせ</a></div>')
MENU_OLD = '<a href="moppy.html">モッピーのページ →</a></nav>'
MENU_NEW = f'<a href="moppy.html">モッピーのページ →</a>{LINK}お問い合わせ</a></nav>'

for folder in ('docs', 'dist'):
    for page in (ROOT / folder).rglob('*.html'):
        if page.name.startswith('google'):
            continue
        text = page.read_text(encoding='utf-8')
        if MARK in text or '</footer>' not in text:
            continue
        text = text.replace('</footer>', BLOCK + '</footer>', 1)
        if page.relative_to(ROOT / folder).as_posix() == 'index.html':
            text = text.replace(MENU_OLD, MENU_NEW, 1)
        page.write_text(text, encoding='utf-8')
print('Contact link added to footers')
