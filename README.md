# POI DAYS — Sitesに依存しない編集用ソース

この一式は、画像追加まで反映した最新保存版（元ソース 393d4a42d3cac0ac150af816cff95e674f0759cc）のコピーです。元のSitesサイト・公開範囲・公開版は変更していません。SitesのAPIキーやSDKは不要です。

## まず表示する

Python 3.10以上があれば、ZIPを展開してこのフォルダで実行します。

```sh
python3 -m http.server 8000 --directory dist
```

ブラウザで http://localhost:8000 を開きます。停止は Ctrl+C。ファイルのダブルクリックではなくHTTPサーバーで確認してください。完成HTMLも同梱しているので、表示だけなら再生成は不要です。

## 編集・再生成

```sh
python3 build.py
python3 check.py
```

- トップの元原稿：`content/home-template.html`
- 案件データ：`content/offers.json`
- 案件の共通テンプレート：`scripts/build-guides.py`
- 解説記事と全体構成：`scripts/expand-site.py`
- 回遊・FAQ・カード：`scripts/enrich.py`
- 独自図解：`scripts/visuals.py`
- デザイン：`dist/style.css`、`dist/enrichment.css`、`dist/visuals.css`
- 診断・試算・コピー・チェックリスト：`dist/app.js`
- 画像：`dist/hero.png`、`dist/visuals/*.svg`

`dist`のHTMLは生成物です。直接直すと次回の再生成で上書きされるため、原稿か生成スクリプトを編集してください。CSSとapp.jsは直接編集して構いません。案件確認日は複数のスクリプトに記載されています。未確認の数値・日付・体験談を作らないでください。

## GitHubで管理する

この環境のGitHub連携には新規リポジトリ作成機能がないため、GitHubリポジトリ自体は未作成です。

1. GitHubで空の `poi-days` リポジトリを作成します。最初はPrivateを推奨。README等は追加せず空で作成。
2. 展開したフォルダで次を実行します。URLは作成したリポジトリのものに置き換えます。

```sh
git init -b main
git add .
git commit -m "Import portable POI DAYS"
git remote add origin https://github.com/YOUR-ACCOUNT/poi-days.git
git push -u origin main
```

GitHubの画面からアップロードする場合はZIPそのものではなく、展開した中身をアップロードします。元のSites用Gitリモートや認証情報は含めていません。Actionsは追加していません。

## 公開先を変える

静的ホスティングに `dist` の内容を配置できます。GitHub Pages用には同じ完成物を `docs` に自動同期します。リンクは相対パスに変換済みで、リポジトリ名のサブパスでも動く構成です。canonicalやサイトマップを作る際は公開先を指定して再生成します。

```sh
SITE_URL=https://100things-project.github.io/poi-days python3 build.py
```

GitHub Pagesでは Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs` を選びます。外部リンクとして必要なモッピー招待URLは維持します。

## 通常チャットへ引き継ぐ

次のチャットにGitHubリポジトリのURL、またはこのZIPを渡して、`HANDOFF.md`を先に読むよう伝えてください。通常チャットで直接GitHubを編集できるかは、そのチャットの接続・書き込み権限に依存します。直接編集できない環境でも、差分や差し替えファイルで作業を続けられます。

## Sitesからそのまま移らないもの

見た目とフロント機能は静的HTML/CSS/JSに含まれます。一方、SitesのURL、所有者限定アクセス、共有設定、保存履歴、公開操作、編集画面はホスティング側の機能であり、GitHubへ自動移行しません。これらを削除したのではなく、元のSites側に残しています。所有者限定アクセスを静的ファイルだけで再現することはできません。公開前に公開範囲を選んでください。

## 検証範囲

再生成一致、12ページの内部リンク・アンカー・招待URL、画像参照・寸法、SVG構文を検証。実ブラウザでの375px/PC表示・コピー操作等は未検証です。元デザインを作り直さず、ホスティング用パスだけを変換しています。
