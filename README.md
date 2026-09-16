# POI DAYS

POI DAYS は、ポイントサイトの案件・使い方・比較・SEO記事をまとめる静的サイトです。現在の本番ソースはこのリポジトリの `main` で管理し、GitHub Pages は **GitHub Actions** から公開します。

公開先: `https://100things-project.github.io/poi-days/`

## 現在の構成

サイトは初期の「12ページ」構成から拡張されています。トップページに加え、モッピーの登録方法・稼ぎ方・紹介コード・評判・安全性などのSEO記事、案件ガイド、ハピタス・ワラウ・ちょびリッチ等のポイントサイト紹介ページを生成・公開します。

主な編集元と生成処理:

- トップの基礎原稿: `content/home-template.html`
- 案件データ: `content/offers.json`
- 日次ランキング: `content/live-rankings.json`
- 日次NEWS: `content/live-news.json`
- ポイントサイト情報: `content/point-sites.json`
- SEO記事: `content/seo/` と `scripts/build-seo.py`
- モッピー内リンク・ナビゲーション: `scripts/build-moppy-internal-links.py`, `scripts/build-moppy-navigation.py`
- CTA: `scripts/add-invite-cta.py`
- GA4/CTA計測: `content/analytics.js` → `scripts/sync-analytics.py` で `dist` / `docs` へ同期
- sitemap `lastmod`: `scripts/add-sitemap-lastmod.py`
- 公開生成物: `dist/` と `docs/`

`dist` / `docs` の生成HTMLを直接直すのではなく、原則として `content/` または生成スクリプトを修正してください。既存デザイン、招待導線、検証済み数値を不要に作り直さないでください。

## ローカルで確認する

通常の再生成は次で行います。

```sh
python3 build.py
python3 check.py
```

表示確認はHTTPサーバー経由で行います。

```sh
python3 -m http.server 8000 --directory dist
```

`http://localhost:8000` を開いて確認します。ファイルのダブルクリックだけで公開相当の確認を済ませないでください。

現在の `build.py` は、既存の公開レイアウトを保護しながら、メディア、ポイントサイト各ページ、ワラウ、ちょびリッチ、モッピー検索導線、SEO、内部リンク、ナビゲーション、CTA、Analytics、sitemap lastmod を順に更新します。旧レイアウト生成は明示的な `--legacy-layout-build` 指定時だけです。

## GitHub Actionsによる公開

`.github/workflows/site-refresh-deploy.yml` が本番公開を担当します。

- `main` への push: 現在のデータでbuild・検証・GitHub Pages公開
- 手動実行: 現在のデータでbuild・検証・公開
- 日次schedule: ランキングとNEWSを各1回取得してからbuild・検証・保存・公開
- production deploy は concurrency で直列化し、実行中の公開を途中キャンセルしません
- queued run は古いpushではなく現在の `main` をcheckoutします
- 公開前に `check.py`、SEO、preservation、media、recommendation、publication guard を通します
- 検証済みデータの保存時は同時編集を上書きしないよう publication guard を使います
- GitHub Pages の Source は **GitHub Actions** です。旧 `main /docs` の branch deploy ではありません

ランキング・NEWS取得に失敗した場合は、前回の有効データを保護する設計を維持します。無限実行やpushループを作らないでください。

## SEO

SEO記事は `content/seo/` と生成スクリプトを正本として扱います。canonical、robots、sitemap、内部リンク、記事更新日はbuild/checkの対象です。

記事本文や `dateModified`、sitemap `lastmod` は、実際に内容を確認・更新した事実に基づいて変更します。Search Consoleの新しい実クエリが十分にない場合、推測だけで記事を増やしたり既存記事を大幅変更しません。

## GA4とCTA計測

GA4 measurement ID は `G-0TZ7EH65BW` です。計測ロジックの正本は `content/analytics.js` です。

現在、招待リンククリック `invite_click` と `cta_location`、診断開始・進捗・完了、外部リンク、内部リンク、案件クリック等をイベントとして送る実装があります。CTAの場所は明示的な `data-cta-location` を優先し、診断結果、記事CTA、キャンペーン、招待パネル、ヒーロー、ヘッダー等を識別します。

計測改善では、CTAをむやみに増やすのではなく、実データを確認して弱い導線だけを調整します。所有者アクセスをGA4から除外する仕組みも `content/analytics.js` にあります。

## 変更時の基本ルール

1. 作業開始時に最新 `main` を確認する。
2. `content/` と生成スクリプトを正本として編集する。
3. `python3 build.py` → `python3 check.py` と関連チェックを通す。
4. preservation guard を壊さない。
5. main反映後はGitHub Actions成功だけで完了とせず、公開された実サイトを開いて対象ページを確認する。
6. 表示崩れ、リンク不良、計測の重大な回帰があれば完了扱いにしない。

より詳しい引き継ぎルールは `HANDOFF.md` を参照してください。
