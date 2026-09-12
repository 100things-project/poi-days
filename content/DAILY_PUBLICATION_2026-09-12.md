# 日次取得・公開経路の移植（2026-09-12）

基準main: 09827b4fca9713d8c4fa34f8fdaf6f4e9f11f2b4（GitHub API確認済）。
前回未保存作業はc48b3e8基準だったため、別worktreeを最新mainから作成して移植した。40ファイルにあった後続更新を保持。旧環境のdocs/distやcollectorは移植していない。

## 構成案と有効化条件

旧ランキング/NEWSの2workflowを1つに統合。
JST 06:05のscheduleでランキングとNEWSを各1回取得し、失敗時は既存collectorが前回正常データを保持する。
ローカルsnapshot書出し → build → 全検証 → snapshot/docs/distを同一commit保存 → docs artifact upload → Pages deploy の順。
永続的なGitHub保存はbuild/検証後に行うため、途中失敗したデータを公開しない。
mainへの通常pushおよび手動再公開は収集なしで検証・保存・公開だけを行う。
同じrun内で公式configure-pages/upload-pages-artifact/deploy-pagesを使う。PATや新たな秘密鍵は不要。

**現在のPages設定の再確認待ちであり、公開方式の変更は未実施。**
前回のユーザー画像ではDeploy from a branch / main /docs。今回Pages設定APIは接続機能の対象外として拒否された。過去画像を最新設定の確認として扱っていない。
採用候補はSource=GitHub Actionsへ切替えてdocs artifactを公開する方式。mainへ入れる前に現在設定の確認と切替の了承が必要。
workflow開始時にもPages APIのbuild_typeがworkflowであることを確認。違えば収集・保存・公開前に失敗する。設定を書き換えるAPIはない。

## 実行回数・競合対策

- 通常は1日1 workflow run / 1 job。JST 06:05予定（GitHub側の遅延はあり得る）。
- 人によるmain pushごとに追加1run。手動復旧時は追加1run。どちらも再収集なし。
- 専用の追加公開workflowやworkflow_run/dispatch連鎖なし。
- GITHUB_TOKENでの生成物pushは別のpush runを起動しない。
- productionの共通concurrency group、cancel-in-progress=falseで同時公開を防ぐ。
- キューから開始したrunはその時点のmainをcheckout。保存前と公開直前にmain SHAを再照合。
- 競合時は停止。rebase・force-push・旧生成物への上書きなし。照合後の通常push競合もGitが拒否する。
- 最終SHA確認とGitHub deploy API間を他者のpushに対して原子的にロックする仕組みではない。その極小区間で更新された場合も新しいmainのpush runが同じキューで後続公開する。
- 失敗した公開は次回scheduleまたは手動の再公開で回復可能。変更がない場合もdeployを省略しない。

## 検証結果

本番Actions・外部collector・Pages deployは今回0回。
check.py（24ページ）、check-seo.py（22URL）、check-preservation.py、check-media.mjs（20ケース）、check-rankings.py、check-news.py、check-collector-fallbacks.py、check-recommendation.py はPASS。
古いテスト期待値：記事5本→7本、検索1件→既存/新規の2URL、sitemap20→22を更新。機能を減らしてテストを通していない。
保全基準は過去のMoppy-only commitから現在checkout HEADへ変更し、全記事・4紹介ページ・紹介設定・画像・GA4・sitemapをbyte比較。日替わり対象のindexとmedia-dataだけ除外する。
公開経路追加テストPASS：schedule/push/manual条件、main限定、検証順序、docs限定artifact、ローカルbare Gitで正常保存・変更なし・他者更新・保存直前raceの拒否、docs/dist不一致・QAファイル・symlinkの拒否。
前回の公開方式テストも移植し、GitHub上の実行や実際のPages/OIDC/環境権限の成功とは区別した。

## 保全・残件

今回docs/dist/contentデータ/記事/紹介設定/collectorに変更なし。新旧取得処理の置換なし。
feat/weekly-featuresは参照・変更・取り込みしていない（最新mainに既に統合済みの成果は維持）。PC版は未着手。
残件：現在Pages設定のスクリーンショット確認、切替の了承と設定操作、mainマージの了承、初回公開成功確認。環境保護ルール・実際のActions書込み権限/OIDCは本番未確認。
判定：コード・ローカル検証は準備済み。現在の公開設定を再確認せずmainへマージ・公開してはいけない。

公式仕様:
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
