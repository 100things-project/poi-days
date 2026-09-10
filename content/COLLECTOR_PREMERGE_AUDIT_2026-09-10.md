# Collector再調査・mainマージ前監査（2026-09-10）

## 開始時のGitHub状態

| ブランチ | commit SHA |
|---|---|
| main | 4d204a18d2e5afc3514a55b45d164268edbbb12c |
| feat/mobile-media-index | 7f2fa8611c2cfb8c7f61ab4a44a34d4da370126d |
| feat/daily-site-rankings | 92d18faa83176a4023bf70e7d07a87c8aa160708 |

GitHub APIで上記を確認。dailyは開始時点でmainより33commit先、遅れなし。mobile→dailyの差分は35ファイル。前回保存内容を再利用し、作り直していない。

## 1. ハピタスランキング

- 公式 https://hapitas.jp/ranking/ は200。静的HTMLの`#item-categorized-ranking`は動的挿入用。
- 現行の公式ranking bundleと参照chunk（5691/807）を確認。公開画面はGET `/api_item-categorized-ranking?limit=60&page=1`を使い、カテゴリごとのitems/update_dateを受け取る構成。
- この公開URLへの認証なしGETは本環境で403。ヘッダー変更・Cookie追加・ログイン・プロキシ等で再試行していない。403の具体的原因は未確定。
- 過去bundleは更新により404だったため、現行HTMLの実在するbundle参照に更新して調査した。
- collectorへのAPI統合は見送り。前回成功データがあれば保持、なければサンプルの安全動作を維持。全カテゴリを総合順位に推測変換しない。

## 2. ちょびリッチランキング

- 公式 https://www.chobirich.com/shopping/ と、そのページが`hx-get`で明示する`/logreco/ranking`の公開HTML断片を確認（いずれも200、ログイン不要）。
- 画面にあるパラメータのみ使用：response_number=15、method_type=2、spot_name=SPShopping_ranking、category1=お買い物で貯める。
- 応答の`ul.CommonRankingBox > li.CommonRankingBox__item`から上位5件を抽出。案件名・現在還元・同一公式ホストの`/ad_details/{数字}`を同一カード内で対応させる。
- 取得結果（2026-09-10）：楽天市場、Yahoo!ショッピング、楽天トラベル（宿泊予約）、楽天ブックス、【リピートOK】iHerb。5件とも1%。全角％は半角%へ表記正規化。
- ショッピング部門であり全サービス総合ではない。snapshotにscopeを保存し、画面に「公式ショッピング順位」と表示。
- 取得した公式HTMLを使ってcollectorを検証し、ちょびリッチのsnapshotだけ更新。他3サイトの取得日を更新していない。
- 公開API契約による安定性保証はない。URL・パラメータ・DOM・必須項目が変われば前回データを保持する。

## 3. モッピーNEWS

- 公式 https://pc.moppy.jp/news/ は200だが一覧は動的。初期パラメータはcategory=0、ym空、page=1。
- 公式JavaScriptにあるGET `/news/list.php?category=0&ym=&page=1`を1回確認：200・本文0byte。
- 公式robotsが案内するsitemap.xmlも確認。NEWS詳細やfeedの掲載なし。旧`/info/`は404。現行NEWSページにRSS/Atomの案内なし。
- 日付・タイトル・公式詳細URLを確実に対応できる一覧を取得できず、統合見送り。FAQ・企業案内・一般キャンペーンページをNEWSへ代用しない。
- 未検証のMoppy汎用anchor/date推測処理を停止。公開一覧の構造が確定するまで未取得または前回成功データ保持。

## 4. 変更内容・回帰検証

- ちょびリッチの公式ページが明示する公開ランキングURLのみ追従。別ホスト・不明なパラメータ・複数候補・構造変更は不採用。
- 共通HTTP処理：HTTPS、同一ホスト、資格情報なし、標準ポートのみ。リダイレクトは最大2回、外部ホストへの追従なし。403やtimeoutの再試行なし。
- ランキング重複URL、不正URL、必須項目欠落を検出。NEWSはHTTPS/同一ホストを検証し重複排除。ワラウは各記事内の日付が欠けたら隣の記事から借りない。
- 4サイト×ランキング/NEWSに対し、403・timeout・0件・HTML変更を通信なしで検証。前回ありは内容と取得日を維持しstale、前回なしはunavailable。
- 正常な1サイトだけ更新し、他サイトの失敗が波及しないことを検証。ランキング不正URL・重複時にも前回内容を保持。
- 本日の正常データだけ日替わりおすすめの対象。stale・過去日・unavailableでおすすめに使わずサンプルへ戻す。
- テストはネットワークを禁止し、保存データが空でも実行できる独立fixtureを使用。

## 5. 指定テスト

次の8検査すべてPASS（本番Actionsは実行していない）。

| 検査 | 根拠 |
|---|---|
| check.py | 22ページ、内部リンク、anchor、招待URL、画像寸法、SVG、再現可能build |
| check-seo.py | metadata、sitemap 20件、shared assets、docs/dist構成 |
| check-preservation.py | main基準の既存保全。以前許可されたリンク移設・Moppy metadataのみ例外 |
| check-media.mjs | 20ケース：タブ、キーボード、欠損、長文、escape、画像fallback等 |
| check-rankings.py | 3取得可能サイトparser、還元、5件、重複/不正URL、公開fragment取得経路 |
| check-news.py | 日付対応、FAQ除外、重複排除、不正URL、Moppy未検証構造の不採用 |
| check-collector-fallbacks.py | 4サイト異常系、前回保持、source isolation、通信回数制限 |
| check-recommendation.py | 現行データと、fresh/stale/過去日/unavailableの独立fixture |

## 6. 実画面確認・保全

Chrome実ブラウザのiframe表示で375/390/430/768pxを確認。全幅でclientWidth=scrollWidth。
各幅のおすすめ・人気サイト・ランキングを実スクリーンショットで確認し、ちょびリッチの選択状態と5件の順位・名称・還元・部門表記も確認。今回追加部分に横はみ出し、欠落、画像崩れなし。CSS/既存完成済みデザインは変更していない。
前回の全セクション/紹介ページQA記録は`QA_MOBILE_2026-09-10.md`。今回の再確認は変更箇所中心で、iPhone実機Safariの確認とは区別する。
`docs`と`dist`は58ファイルすべてbyte一致。今回、既存Moppyページ・既存記事・guide・画像・GA4・point-sitesの招待情報に差分なし。

## 7. mainとの差分・公開影響

- mainのトップは既存Moppy中心ページ。dailyを公開すると総合メディアIndexへ変わり、ランキング・NEWS・おすすめ・人気サイト・3サイト紹介ページが追加される。
- 既存記事本文/画像/招待/GA4は保全。main→daily全体では、以前実装した記事・guide内のMoppy固有anchorを`moppy.html`へ向ける変更とMoppy専用metadata変更がある。今回新たに記事本文を変更したものではない。
- sitemapに新Index系統ページが追加される。ファイル削除、履歴書換え、破壊的データ移行なし。
- 開発用package-lock/Vite、build script、回帰テスト、content内監査記録はGitHubに保存されるが、docsを公開元とする場合は配信対象外。
- 一時QA画面、取得元のraw HTML/JavaScript、端末ログ、依存ディレクトリはcommitへ入れない。
- 差分の資格情報パターン検査でtoken/API key/秘密鍵なし。公開用GA測定ID・招待URLは秘密鍵と区別し保全。検査で未知形式の秘密情報まで不存在を保証するものではない。

## 8. workflow監査・公開前の要確認

- mainに新規追加される2workflow：daily-rankings（JST 00:05）、point-site-news（JST 06:05）。各1日1回。workflow_dispatch定義はあるが今回実行していない。
- scheduleはdefault branchにファイルが存在するときだけ動く。開始時のdefault branchはmain。現ブランチへの保存だけではscheduleは有効にならない。
- 両workflowは共通concurrency groupへ変更。生成物への同時書込みを直列化。手動/他者commitと衝突したpushはforceせず失敗する。
- contents:write、timeout 10分、依存はrequests/BeautifulSoupの固定version。新しいsecrets不要。
- collectorの異常系回帰チェックを両workflowに追加。生成後のcheck.pyで検証してからsnapshot/docs/distだけcommit。
- **公開運用の未解決点：GITHUB_TOKENによるpushは、ブランチを公開元とするGitHub Pages buildを起動しない。** 現workflowにはPagesデプロイ処理がない。保存成功と公開更新成功は別であり、毎日の画面更新を保証できない。
- 実際の現在のPages設定を今回APIで独立確認したわけではない。既知のmain/docs方式で運用を続けるなら、公開方法の設計・承認が必要。無断でPages設定変更やデプロイworkflow追加/実行をしない。
- GitHub公式根拠：https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- GitHub公式根拠：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## 9. weekly-featuresとの将来競合

内容・patchは開いていない。refとcompareのcommit/ファイル名メタデータだけ確認。
調査時SHA：7000232a392ad58927bdde1735a0611a60ccd838。共通祖先aef331df9b237fe831d4225f5a10e88f99974564。開始時daily固有1commit、weekly固有21commit。
weekly側の分岐後変更名はcontent/media-home.json、scripts/build-seo.py、新記事・記事一覧・article-prose.css（docs/dist）など11ファイル。
分岐後のdaily変更との同名ファイル重複は今回もなし。ただし内容を見ない確認のため、意味上の整合性や将来のmerge成功は保証しない。統合時は新記事の出力保持、Index掲載、sitemap件数の再ビルド検証が必要。中身の確認が必要になったら別途確認を求める。weeklyをcheckout/fetch/変更/取り込みしていない。

## 10. 判定・未完了

**mainマージはまだ待つ。** collectorと異常系の修正は保存できる状態だが、毎日取得した結果をPagesへ反映する公開方式の確認が残る。
未取得はハピタスランキングとモッピーNEWS。安全なfallbackは確認済みだが、4サイト完全自動取得としての完成ではない。
前回Moppy snapshotの楽天銀行はタイトルに12,000P、還元欄に1,500Pという公式内不一致が残る。今回は正常取得済みサイトを再収集していないため、公開判断時の確認対象として維持。
本番Actions、mainマージ、Pages公開、PC版制作は実施していない。
