"""Show both publish and update dates on SEO articles when they differ."""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
changed = 0


def jp_date(value):
    year, month, day = (int(x) for x in value.split('-'))
    return f'{year}年{month}月{day}日'


for base in (ROOT / 'docs' / 'articles', ROOT / 'dist' / 'articles'):
    for path in sorted(base.glob('moppy-*.html')):
        text = path.read_text(encoding='utf-8')
        match = re.search(
            r'<script type="application/ld\+json" data-poidays-schema>(.*?)</script>',
            text,
        )
        if not match:
            continue
        schema = json.loads(match.group(1))
        article = next(
            (item for item in schema.get('@graph', []) if item.get('@type') == 'Article'),
            None,
        )
        if not article:
            continue
        published = article.get('datePublished')
        modified = article.get('dateModified')
        if not published or not modified or modified <= published:
            continue

        old = (
            f'<p class="seo-date">公開・情報確認：<time datetime="{published}">'
            f'{jp_date(published)}</time>　編集：POI DAYS</p>'
        )
        new = (
            f'<p class="seo-date">公開：<time datetime="{published}">{jp_date(published)}</time>'
            f'　更新・情報確認：<time datetime="{modified}">{jp_date(modified)}</time>'
            f'　編集：POI DAYS</p>'
        )
        if old not in text:
            raise SystemExit(f'Expected SEO date line not found: {path}')
        path.write_text(text.replace(old, new, 1), encoding='utf-8')
        changed += 1

print(f'SEO visible update dates added: {changed} generated files')
