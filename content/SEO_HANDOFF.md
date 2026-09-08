# SEO 5記事制作 — 2026-09-08

## 基準

初回はmain `06b84966bc96098e26cb73466086741fd887f2ec`。再開時は最新main `f6aa746dbad83ec1e0e5b3af09519d7f014a9f20` と照合。ヒーロー・交換先・診断・ランキングのHTML/CSS/JSは変更しない。

再開時の判定：調査・5記事・内部リンク・初回公開は完了済み。スマホ検証・公開回帰確認は途中。最新mainの解析/構造化データと生成処理の整合、検証ページ撤去、最終記録は未着手だった。本文を作り直さず、これらを実施した。

## ビルド

`python3 build.py` は現在 `scripts/build-seo.py` を実行する。旧レイアウト生成元に未反映の公開版修正があるため、既存docsを静的ベースとして保持し、5記事と一覧、記事CSS、既存4記事の関連導線、sitemapのみ再生成する。

本文：`content/seo/*.html`。共通HTML：`content/seo-template.html`。記事CSS：`content/seo-articles.css`。SEOタイトル・説明文・関連記事：`scripts/build-seo.py`。

従来の `--legacy-layout-build` はレイアウト全体を再生成するため、今回の作業では使用しない。他作業の直接編集を消すおそれがある。通常ビルドはdocs/distの予期しない不一致を検出すると停止する。

既存docsの交換先画像4枚とSearch Console確認ファイルはdistへ同一内容で複製。既存トップ・CSS・JSはそのまま。既存GA4 IDは新記事にも維持。

## 調査と執筆方針

確認日：2026-09-08。公式ガイド、利用規約、会社概要、セレス2026-03-18発表、友達紹介ヘルプ、登録入口、アプリ広告、追跡未反映ヘルプを参照。各記事内に該当出典を配置。

口コミ：App Store（2020-10-16 牢屋から脱出成功、2021-01-08 ＊6 と運営回答）、みん評（2026-08-29 とも、2025-07-25 オレオ）を短く要約。全件集計・多数派推定・体験談作成はしていない。閲覧できなかった投稿本文は使用していない。投稿は独立検証されていないことを明記。

変動情報：会員規模・運営情報・1P価値・登録方法・年齢・紹介成立条件・ゲーム計測条件・退会導線に確認日。個別ゲームの最新ランキング、還元額、達成時間は未確認のため作成しない。

登録フォームを実際に送信していない。個別紹介キャンペーン画面の適用は利用者が登録時に確認。固定特典額や保証表現は使わない。

## 必須検証チェックリスト

- [x] 指示書の本文・全表を全文確認し、作業前チェックリスト提示
- [x] 最新main基準の変更差分確認
- [x] 5テーマの公式調査、口コミ複数投稿の確認
- [x] 5記事本文・目次・結論・要点/注意/手順・関連記事
- [x] 各記事固有のtitle/H1/90〜130字description
- [x] 指定紹介URL/code・PR/報酬表示・特典非保証
- [x] パンくず・記事内/末尾2件のリンク・診断/ランキング導線
- [x] 生成元/テンプレート/ビルド実装
- [x] 内部リンク・アンカー・紹介URLの静的検査
- [x] 公開5URL直接表示
- [x] 375pxの全記事表示・重なり・横幅確認
- [x] PC表示確認
- [x] 外部リンク到達確認（下記に到達手段と制限を記録）
- [x] 公開版診断・ランキング・交換先の回帰確認
- [x] 一時検証ページの削除と最終dist/docs一致（公開撤去確認はデプロイ後）
- [x] 完了時に全項目を照合し、未確認を明示

## 実測結果

2026-09-08、GitHub Pages公開版をChromeで確認。375pxのiframe内で各記事の見出し・本文カード・末尾CTA/関連記事を確認。5記事すべて文書のclientWidth/scrollWidthは360/360（スクロールバーを含む表示幅375）。安全性・口コミ・稼ぎ方・ゲームではmain配下要素の右端はみ出しもなし。記事に固定CTAはなく、本文末尾リンクを覆う要素なし。PCは約1363px、本文最大760pxで確認。iPhone実機/Safariそのものの確認ではない。

トップも375pxで360/360。既存カード写真、ランキングの図解、交換先の図解を表示確認。診断は初期0/5・結果ボタン無効からテスト回答5/5に進み、「いつもの買い物で、コツコツ型」が表示された。テスト回答は利用者の実情報ではない。トップ/主要CSS/JS/ヒーロー/解析/プライバシー/Search Consoleファイルは最新mainとのバイト一致検査に合格。

外部リンク：公式・会社・App Store・指定紹介URLの20 URLがHTTP 200。みん評は自動HTTP取得が403だが、調査時の検索閲覧で使用した投稿本文と日付を確認済み。実会員登録・認証・特典適用や個別案件達成は行っていない。

最終ローカル検査：`python3 build.py`、`python3 check.py`、`python3 scripts/check-seo.py` 合格。18ページの内部リンク/アンカー/画像寸法、5記事固有メタ情報、指定紹介URL、構造化データ、再ビルド再現性、docs/dist全ファイル一致。sitemapは16の正規URL（旧安全性/登録ページは新記事へcanonical、検証ページは除外）。

## 5記事と検索意図

| SEOタイトル（末尾に「｜POI DAYS」） | 主検索意図 | URL |
|---|---|---|
| モッピーとは？怪しい？安全性・仕組みを初心者向けに解説 | モッピーとは・怪しい・安全・危険性 | https://100things-project.github.io/poi-days/articles/moppy-safety.html |
| モッピーの評判・口コミ｜良い評判と悪い評判を整理 | 評判・口コミ・悪い評判 | https://100things-project.github.io/poi-days/articles/moppy-reviews.html |
| モッピーの稼ぎ方｜初心者が最初にやること | 稼ぎ方・初心者・貯め方 | https://100things-project.github.io/poi-days/articles/moppy-earning.html |
| モッピーの登録方法｜招待コード・紹介リンクの使い方 | 登録方法・招待コード・紹介コード | https://100things-project.github.io/poi-days/articles/moppy-registration.html |
| モッピーのゲーム案件｜初心者向けの選び方・注意点 | ゲーム案件・選び方・注意点 | https://100things-project.github.io/poi-days/articles/moppy-games.html |

## 主要公式情報源

- https://pc.moppy.jp/guide/ （仕組み・1P価値・開始年）
- https://pc.moppy.jp/rule/ （会員条件）
- https://pc.moppy.jp/entry/ （登録入口）
- https://pc.moppy.jp/help/?category_id=16 （友達紹介）
- https://pc.moppy.jp/help/?category_id=19 （アプリ広告）
- https://pc.moppy.jp/help/?category_id=25 （顔認証）
- https://pc.moppy.jp/st/info/tracking/ （未反映の確認）
- https://pc.moppy.jp/st/info/corporate/ （運営会社）
- https://ceres-inc.jp/news/detail/20260318-2/ （累計会員数発表）

## 内部リンク

安全性→口コミ/稼ぎ方/トップ特徴/診断、口コミ→安全性/登録/診断、稼ぎ方→ゲーム/登録/ランキング/診断、登録→稼ぎ方/ゲーム/トップ、ゲーム→稼ぎ方/登録/ランキング/診断。各記事の末尾は関連記事2件。既存about/safety/registration/categoriesから新記事・初心者一覧へも接続。

## 変更ファイル

初回成果物：`content/seo/*.html`（5本文）、`content/seo-template.html`、`content/seo-articles.css`、`scripts/build-seo.py`、`scripts/check-seo.py`、`build.py`、`check.py`、`docs`/`dist`の `articles/moppy-*.html`、`articles/index.html`、`seo-articles.css`、既存4記事の関連導線、`sitemap.xml`、`robots.txt`、この記録。

今回の続き：`scripts/build-seo.py`（最新mainのschema・正規トップリンク・canonical別sitemapを再現）、`scripts/check-seo.py`（最新main保全/解析/schema検査）、`check.py`（ディレクトリURLのアンカー検査）、この記録。最新docsをdistの `index.html`、`analytics.js`、`sitemap.xml`、全12記事、全5攻略記事へ同期。`docs/qa-preview.html`・`dist/qa-preview.html`を撤去。公開記事本文・トップデザインの変更なし。

## 明示的な未確認・対象外

実機Safari、会員登録/認証/紹介特典の実適用、個別ゲーム達成、検索順位・流入・成約の改善実績は未確認。トップの案件ランキングは既存の9月5日確認記録を維持し、今日の順位に更新したとは扱わない。今回の5記事検証とは別の運用作業となる。
