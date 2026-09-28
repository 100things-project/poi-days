"""Add shared reader-trust components to generated and preserved pages.

Runs after the article/CTA generators. Every insertion is wrapped in a marker
and rebuilt from scratch, so repeated builds produce identical bytes.

- Article summary box (結論まとめ) from content/article-summaries.json
- Moppy cluster: 3-level breadcrumb via the hub page (HTML + BreadcrumbList)
  and a shared "related articles" block
- Visible PR label on article disclosures and a PR bar on other pages that
  contain sponsored referral links
- Links to the operator/editorial-policy page where a page has none
- Operator details on the policy page, only for fields that are filled in
- Storage-safe owner-exclusion snippet for preserved pages with inline gtag
"""
from pathlib import Path
import html, json, os, re

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = (ROOT / 'docs', ROOT / 'dist')
BASE = os.environ.get('SITE_URL', 'https://100things-project.github.io/poi-days').rstrip('/')
SUMMARIES = {k: v for k, v in json.loads((ROOT / 'content/article-summaries.json').read_text(encoding='utf-8')).items() if not k.startswith('_')}
OPERATOR = json.loads((ROOT / 'content/site-operator.json').read_text(encoding='utf-8'))
POINT_SITES = json.loads((ROOT / 'content/point-sites.json').read_text(encoding='utf-8'))
CSS_VERSION = '20260928-2'
HUB = 'moppy-guide'
HUB_TITLE = 'モッピー初心者ガイド'

# Reading order used by the related-articles block (matches the hub page).
CLUSTER = [
 ('登録前に確認', [('moppy-safety', '安全性・運営会社'), ('moppy-reviews', '評判・口コミ'), ('moppy-pros-cons', 'メリット・デメリット')]),
 ('登録する', [('moppy-referral-code', '紹介コードの入力場所'), ('moppy-september-campaign', '9月のキャンペーン'), ('moppy-registration', '登録方法'), ('moppy-registration-trouble', '登録できないとき')]),
 ('始める・困ったとき', [('moppy-earning', '初心者の稼ぎ方'), ('moppy-games', 'ゲーム案件の選び方'), ('moppy-points-missing', 'ポイントが付かないとき')]),
]


def marked(name, body):
 return f'<!-- POIDAYS:{name} -->{body}<!-- /POIDAYS:{name} -->'


def strip(name, text):
 return re.sub(rf'<!-- POIDAYS:{name} -->.*?<!-- /POIDAYS:{name} -->', '', text, flags=re.S)


def summary_box(lines):
 items = ''.join(f'<li>{html.escape(line)}</li>' for line in lines)
 return marked('summary', f'<aside class="seo-summary" aria-label="この記事の結論まとめ"><p class="seo-summary-title">この記事の結論まとめ</p><ul>{items}</ul></aside>')


def related_block(current):
 groups = []
 for label, links in CLUSTER:
  items = ''.join(
   f'<li><span aria-current="page">{html.escape(text)}（この記事）</span></li>' if slug == current
   else f'<li><a href="{slug}.html">{html.escape(text)}</a></li>'
   for slug, text in links)
  groups.append(f'<div><p>{label}</p><ul>{items}</ul></div>')
 return marked('related', '<section class="seo-related" aria-labelledby="seo-related-title"><h2 id="seo-related-title">モッピーの関連記事</h2>'
               f'<div class="seo-related-groups">{"".join(groups)}</div>'
               f'<a class="seo-related-hub" href="{HUB}.html">読む順番は{HUB_TITLE}で確認 →</a>'
               '<div class="seo-related-sites"><p>ほかのポイントサイトと比べる</p><ul>'
               '<li><a href="point-site-selection.html">ポイントサイトの選び方</a></li>'
               '<li><a href="../hapitas.html">ハピタス</a></li><li><a href="../warau.html">ワラウ</a></li>'
               '<li><a href="../chobirich.html">ちょびリッチ</a></li></ul></div></section>')


def moppy_breadcrumb(text, slug):
 """Insert the hub between the article index and the article, in HTML and schema."""
 if slug == HUB:
  return text
 hub_link = f'<a href="{HUB}.html">{HUB_TITLE}</a><span>›</span>'
 old = '<a href="index.html">初心者ガイド</a><span>›</span>'
 if hub_link not in text:
  if old not in text:
   raise SystemExit(f'breadcrumb anchor not found: {slug}')
  text = text.replace(old, old + hub_link, 1)
 match = re.search(r'(<script type="application/ld\+json" data-poidays-schema>)(.*?)(</script>)', text, re.S)
 schema = json.loads(match[2])
 for item in schema['@graph']:
  if item.get('@type') == 'BreadcrumbList':
   url = next(x['url'] for x in schema['@graph'] if x.get('@type') == 'Article')
   headline = next(x['headline'] for x in schema['@graph'] if x.get('@type') == 'Article')
   item['itemListElement'] = [
    {'@type': 'ListItem', 'position': 1, 'name': 'POI DAYS', 'item': BASE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': '初心者ガイド', 'item': BASE + '/articles/index.html'},
    {'@type': 'ListItem', 'position': 3, 'name': HUB_TITLE, 'item': f'{BASE}/articles/{HUB}.html'},
    {'@type': 'ListItem', 'position': 4, 'name': headline, 'item': url}]
 payload = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
 return text[:match.start()] + match[1] + payload + match[3] + text[match.end():]


def hub_breadcrumb_schema(text):
 match = re.search(r'(<script type="application/ld\+json" data-poidays-schema>)(.*?)(</script>)', text, re.S)
 schema = json.loads(match[2])
 for item in schema['@graph']:
  if item.get('@type') == 'BreadcrumbList':
   last = item['itemListElement'][-1]
   item['itemListElement'] = [
    {'@type': 'ListItem', 'position': 1, 'name': 'POI DAYS', 'item': BASE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': '初心者ガイド', 'item': BASE + '/articles/index.html'},
    {'@type': 'ListItem', 'position': 3, 'name': last['name'], 'item': last['item']}]
 payload = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
 return text[:match.start()] + match[1] + payload + match[3] + text[match.end():]


def schema_author_links(text):
 """Point author/publisher at the editorial-policy page (same organization)."""
 match = re.search(r'(<script type="application/ld\+json" data-poidays-schema>)(.*?)(</script>)', text, re.S)
 if not match:
  return text
 schema = json.loads(match[2])
 for item in schema.get('@graph', []):
  if item.get('@type') == 'Article':
   item['author'] = {'@type': 'Organization', 'name': 'POI DAYS', 'url': BASE + '/articles/policy.html'}
   item['publisher'] = {'@type': 'Organization', 'name': 'POI DAYS', 'url': BASE + '/'}
 payload = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
 return text[:match.start()] + match[1] + payload + match[3] + text[match.end():]


def pr_bar(prefix, extra=''):
 style = ('<style>.poidays-pr{display:flex;gap:10px;align-items:flex-start;margin:0;padding:10px 16px;'
          'background:#fff7ea;border-bottom:1px solid #f1d2b0;color:#5b4636;font-size:13px;line-height:1.7}'
          '.poidays-pr b{flex:none;background:#d97822;color:#fff;border-radius:4px;padding:0 7px;font-size:12px;line-height:1.8}'
          '.poidays-pr a{color:#145951;text-decoration:underline}</style>')
 return marked('pr', f'{style}<p class="poidays-pr"><b>PR</b><span>このページには紹介リンクを含みます。紹介リンク経由の登録・利用により、POI DAYS運営者が報酬を受け取る場合があります。{extra}'
                     f'<a href="{prefix}articles/policy.html">運営情報・編集方針</a></span></p>')


def trust_links(prefix):
 style = ('<style>.poidays-trust{max-width:760px;margin:0 auto;padding:18px 20px 28px;display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px}'
          '.poidays-trust a{color:#145951;text-decoration:underline}</style>')
 return marked('trust', f'{style}<nav class="poidays-trust" aria-label="運営情報"><a href="{prefix}articles/policy.html">運営情報・編集方針</a>'
                        f'<a href="{prefix}articles/privacy.html">プライバシーポリシー</a><a href="{prefix}articles/index.html">記事・特集一覧</a></nav>')


def jp_date(value):
 y, m, d = (int(x) for x in value.split('-'))
 return f'{y}年{m}月{d}日'


def operator_block():
 def lines(value):
  values = value if isinstance(value, list) else [value]
  return [v for v in values if isinstance(v, str) and v.strip() and not v.startswith('【要記入')]
 fields = [('運営者', OPERATOR.get('operatorName', '')), ('お問い合わせ', OPERATOR.get('contact', '')), ('運営者プロフィール', OPERATOR.get('editorProfile', ''))]
 filled = [(k, lines(v)) for k, v in fields if lines(v)]
 editorial = ('<section><h2>記事の作り方</h2><ul>'
              '<li>ポイントサイトの条件・キャンペーンは、公式ヘルプや公式発表を確認し、記事内に確認日と出典を記載します。</li>'
              '<li>記事には公開日と、内容を確認・更新した日を表示します。</li>'
              '<li>口コミは投稿者個人の申告として扱い、公式情報と分けて紹介します。POI DAYSが体験していないことを体験談として書きません。</li>'
              '<li>紹介リンクを含むページには「PR」を表示します。報酬の有無によって記事の評価を変えません。</li>'
              '</ul></section>')
 details = ''
 if filled:
  details = ('<style>.poidays-operator dt{font-weight:700;color:#145951;margin-top:14px}.poidays-operator dd{margin:4px 0 0}.poidays-operator dd p{margin:0 0 8px}</style>'
             '<section><h2>運営者情報</h2><dl class="poidays-operator">' + ''.join(f'<dt>{html.escape(k)}</dt><dd>' + ''.join(f'<p>{html.escape(v)}</p>' for v in vs) + '</dd>' for k, vs in filled) + '</dl></section>')
 return marked('operator', editorial + details)


# Update dates for preserved (non-generated) articles.
STATIC_MODIFIED = {'point-site-selection': '2026-09-28', 'game-offer-selection': '2026-09-28'}


def set_static_modified(text, modified):
 shown = f'<time datetime="{modified}">{jp_date(modified)}</time>'
 text = re.sub(r'(<script type="application/ld\+json">[^<]*?"dateModified":")[^"]+(")', rf'\g<1>{modified}\2', text, count=1)
 if re.search(r'<p class="seo-date">[^<]*?公開：<time[^>]*>[^<]*</time>　更新：<time', text):
  return re.sub(r'(<p class="seo-date">[^<]*?公開：<time[^>]*>[^<]*</time>　更新：)<time[^>]*>[^<]*</time>', lambda m: m[1] + shown, text, count=1)
 new, n = re.subn(r'<p class="seo-date">公開・情報確認：(<time[^>]*>[^<]*</time>)', lambda m: f'<p class="seo-date">公開：{m[1]}　更新：{shown}', text, count=1)
 assert n == 1, 'static article date line not found'
 return new


# about.html / categories.html are consolidated into newer guides (noindex +
# canonical in build-seo.py). Point internal links at the newer pages.
LEGACY_LINKS = [
 (r'articles/categories\.html#part-0|categories\.html#part-0', 'moppy-games.html'),
 (r'articles/categories\.html#part-1|categories\.html#part-1', 'moppy-earning.html#free'),
 (r'articles/categories\.html(?:#part-\d)?|categories\.html(?:#part-\d)?', 'moppy-earning.html#categories'),
 (r'articles/about\.html|about\.html', 'moppy-guide.html'),
]


def retarget_legacy_links(text, rel):
 def fix(match):
  href = match[1]
  prefix = href[:len(href) - len(href.lstrip('./'))]
  body = href[len(prefix):]
  for pattern, target in LEGACY_LINKS:
   if re.fullmatch(pattern, body):
    path = ('articles/' if body.startswith('articles/') else '') + target
    return f'href="{prefix}{path}"'
  return match[0]
 return re.sub(r'href="((?:\.\./)*(?:articles/)?(?:about|categories)\.html(?:#part-\d)?)"', fix, text)


GTAG_OLD = "if(p.get('owner')==='1')localStorage.setItem(k,'1');if(p.get('owner')==='0')localStorage.removeItem(k);if(localStorage.getItem(k)==='1')window['ga-disable-G-0TZ7EH65BW']=true;if(p.has('owner'))"
GTAG_NEW = "try{if(p.get('owner')==='1')localStorage.setItem(k,'1');if(p.get('owner')==='0')localStorage.removeItem(k);if(localStorage.getItem(k)==='1')window['ga-disable-G-0TZ7EH65BW']=true;}catch(e){}if(p.has('owner'))"


def process(folder, path):
 rel = path.relative_to(folder).as_posix()
 text = original = path.read_text(encoding='utf-8')
 for name in ('summary', 'related', 'pr', 'trust', 'operator'):
  text = strip(name, text)
 prefix = '../' * rel.count('/')
 has_policy_link = 'policy.html' in text
 slug = path.stem
 is_article = 'class="seo-disclosure"' in text

 text = text.replace(GTAG_OLD, GTAG_NEW)
 if rel not in ('articles/about.html', 'articles/categories.html'):
  text = retarget_legacy_links(text, rel)
 text = re.sub(r'seo-articles\.css(\?v=[^"]*)?"', f'seo-articles.css?v={CSS_VERSION}"', text)

 if is_article:
  text = text.replace('<p class="seo-disclosure">PR：', '<p class="seo-disclosure"><span class="pr-badge">PR</span>')
  if slug in STATIC_MODIFIED and not rel.startswith('articles/moppy-'):
   text = set_static_modified(text, STATIC_MODIFIED[slug])
  if slug in SUMMARIES:
   text, n = re.subn(r'(<p class="seo-disclosure">.*?</p>)', lambda m: m[1] + summary_box(SUMMARIES[slug]), text, count=1, flags=re.S)
   assert n == 1, rel
  text = schema_author_links(text)
  if rel.startswith('articles/moppy-'):
   if slug == HUB:
    text = hub_breadcrumb_schema(text)
   else:
    text = moppy_breadcrumb(text, slug)
    text, n = re.subn(r'</main>', lambda m: related_block(slug) + '</main>', text, count=1)
    assert n == 1, rel
 elif 'rel="sponsored' in text and rel.count('/') <= 1 and not rel.startswith('google'):
  extra = ''
  site = next((s for s in POINT_SITES.get('sites', []) if s.get('page') == rel), None)
  # moppy.html is a preserved page with its own dated sources; only pages
  # generated from point-sites.json show that file's check date.
  if site and site.get('id') != 'moppy' and POINT_SITES.get('checkedAt'):
   extra = f'掲載情報の確認日：{jp_date(POINT_SITES["checkedAt"])}。'
  header_end = re.search(r'</header>', text)
  if not header_end:
   raise SystemExit(f'header not found for PR bar: {rel}')
  text = text[:header_end.end()] + pr_bar(prefix, extra) + text[header_end.end():]

 if not has_policy_link:
  text = text.replace('</body>', trust_links(prefix) + '</body>', 1)

 if rel == 'articles/policy.html':
  anchor = '<p class="source">参考：'
  if anchor not in text:
   raise SystemExit('policy page anchor not found')
  text = text.replace(anchor, operator_block() + anchor, 1)

 if text != original:
  path.write_text(text, encoding='utf-8')
  return 1
 return 0


changed = 0
for folder in FOLDERS:
 for path in sorted(folder.rglob('*.html')):
  if path.name.startswith('google') or path.name == 'qa-preview.html':
   continue
  changed += process(folder, path)
 assert (folder / f'articles/{HUB}.html').exists()
print(f'Article trust components applied: {changed} files updated (summaries, hub breadcrumbs, related links, PR labels, policy links)')
