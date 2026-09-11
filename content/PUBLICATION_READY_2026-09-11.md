# POI DAYS 新Index 公開前統合確認（2026-09-11）

- 統合元: `feat/daily-site-rankings` の最新保存点 `c48b3e8c19027a4338408b081ebb3518959f57d4`
- 統合先: `feat/index-publication-integration`
- `feat/weekly-features` から一般記事2本・記事ハブ・特集データを統合
- `content/media-home.json` は新Indexのランキング/NEWS構造を保持したまま、特集・新着記事を統合
- 新Indexに「ポイントサイトの選び方」「ゲーム案件の選び方」が表示されることを生成結果で確認
- `docs` と `dist` はビルドで同期
- ランキング検証 PASS
- NEWS検証 PASS
- 今日のおすすめ案件検証 PASS
- collector fallback検証 PASS
- 全リンク・アンカー・紹介URL・画像属性・SVG・再現ビルド検証 PASS
- 一般記事の `../#popular-sites` 不整合を `../#popular` に修正
- 一時検証workflowは削除済み
- ランキング/NEWSの自動公開方式はWork復帰後に完成予定。そこまでは手動更新運用

公開前の残件は、mainへ統合後のGitHub Pages反映確認とiPhone Safari実機QA。
