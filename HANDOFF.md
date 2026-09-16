# 次の編集者へ

目的：現在の POI DAYS を壊さず、最新 `main` を正本として継続編集する。

## 作業開始時

- 必ず最新 `main` を確認してから作業する。古い Work 環境や生成物で `main` を上書きしない。
- まず `README.md` とこの `HANDOFF.md` を読む。
- 通常の再生成・基本検証は `python3 build.py` → `python3 check.py` の順で行う。
- 変更内容に応じて SEO、preservation、media、recommendation、publication の各チェックも通す。
- `dist/` / `docs/` の生成 HTML を正本として直接編集せず、原則 `content/` または生成スクリプトを修正する。

## 現在の公開方式

- 本番は GitHub Pages。Source は **GitHub Actions**。
- `.github/workflows/site-refresh-deploy.yml` が production build / validation / deploy を担当する。
- `main` への push と手動実行では現在データを build・検証・公開する。
- 日次 schedule はランキングと NEWS を各1回取得してから build・検証・保存・公開する。
- production deploy は concurrency で直列化し、実行中の公開を途中キャンセルしない。
- queued run は古い push revision ではなく現在の `main` を checkout する。
- 公開前に `check.py`、SEO、preservation、media、recommendation、publication guard を通す。
- GitHub Actions の成功や artifact 作成だけで、公開サイトの表示確認済みとは扱わない。公開 UI を変えた場合は実サイトも確認する。

## 日次ランキング・NEWS

- 日次ランキング: `content/live-rankings.json`
- 日次 NEWS: `content/live-news.json`
- 取得処理: `scripts/fetch-rankings.py`, `scripts/fetch-news.py`
- 取得失敗時は前回の有効データを保護する。失敗を空データや推測値で上書きしない。
- 無限実行、push ループ、不要な Actions 消費を増やさない。
- 同時編集を壊さないため `scripts/publication.py` の publication guard を維持する。

## CTA・GA4 計測

- 計測ロジックの正本は `content/analytics.js`。
- GA4 measurement ID は `G-0TZ7EH65BW`。
- `scripts/sync-analytics.py` で生成物へ同期する。
- 現在は `invite_click` と `cta_location`、`invite_copy`、`moppy_offer_click`、`diagnosis_start` / `diagnosis_progress` / `diagnosis_complete`、`planner_complete`、`outbound_click`、`internal_link_click`、`faq_open` などを送る。
- CTA の場所は `data-cta-location` を優先し、診断結果、記事 CTA、キャンペーン、招待パネル、ヒーロー、ヘッダー等を識別する。
- CTA は実データを見て弱い導線だけ改善し、むやみに増やさない。
- 所有者アクセス除外の仕組みを壊さない。

## SEO・sitemap

- SEO 記事の正本は `content/seo/` と `scripts/build-seo.py`。
- canonical、robots、sitemap、内部リンク、記事更新日は build/check の対象。
- sitemap `lastmod` は `scripts/add-sitemap-lastmod.py` で扱う。
- `dateModified` と sitemap `lastmod` は、実際に内容を確認・更新した事実に基づいて変更する。
- Search Console の新しい実クエリが十分にない場合、推測だけで記事を増やしたり大幅改変しない。
- 既存記事との検索意図重複・カニバリを確認してから新規記事を追加する。

## preservation / publication guard

- 既存デザイン、招待導線、検証済み数値、保存済みコンテンツを不要に作り直さない。
- `scripts/check-preservation.py` と `scripts/publication.py` の安全装置を外さない。
- 日次データ保存時に同時編集を上書きしない。
- build が成功しても preservation / publication の検証に失敗した変更は公開しない。

## 触ってよい場所

- トップの基礎原稿: `content/home-template.html`
- 案件データ: `content/offers.json`
- 日次データ: `content/live-rankings.json`, `content/live-news.json`
- ポイントサイト情報: `content/point-sites.json`
- SEO記事: `content/seo/`
- Analytics: `content/analytics.js`
- 必要な生成・検証スクリプト: `scripts/`

変更は目的に必要な最小範囲に留め、生成元を直した後に build で `dist/` / `docs/` へ反映する。

## 壊してはいけないもの

- 色・ロゴ・ヒーロー・既存 UI を理由なく全面変更しない。
- 招待 URL / 招待コード、CTA 導線、既存の計測属性を無断で変更しない。
- 検証済み案件データを推測値で置き換えない。
- `dist/` / `docs/` だけを手編集して生成元との不整合を作らない。
- Pages の公開方式を旧 `main /docs` branch deploy に戻さない。
- preservation / publication guard を回避しない。
- 自動更新・人気実績・実利用経験を捏造しない。

## 公開後の確認

- README / HANDOFF のような内部ドキュメントは、最新 `main` 上の内容・差分・整合性・必要な回帰確認で完了判定する。
- HTML / CSS / JS / CTA / 記事 / ナビゲーション / 画像 / レイアウトなどユーザーが見る変更は、GitHub Actions 成功だけで完了にせず、公開された実サイトを開いて対象変更を確認する。
- スマホ QA は 375 / 390 / 430 / 768px を中心に、横はみ出し、CTA 折返し、画像切れ、余白、記事上部の密度、タップ領域を確認する。
- PC QA はトップ、モッピー TOP、登録方法、稼ぎ方、紹介コード、評判、安全性を確認する。
- 実サイトを確認できない場合は、視覚確認が必要な項目を完了扱いにしない。確認できないこと自体を「問題なし」としない。

## 現在の主な残課題

- スマホ / PC の実表示 QA。
- CTA クリック計測と `cta_location` の分析可否確認。
- Search Console の最新実クエリを基準にした次記事判断。
- 5問診断の完了率と診断結果から登録クリックへの遷移確認。
- 公開問い合わせ窓口とスポンサー募集ページの整備。
- ランキング・NEWS 日次更新の継続監視。
- 必要な SEO 記事だけを公式情報に基づいて更新し、モッピーで確立した型を需要に応じて他ポイントサイトへ横展開する。

最終 KPI は、単なるページ数ではなく **表示 → 記事閲覧 → CTAクリック → 登録** の導線改善とする。
