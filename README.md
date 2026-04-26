# feed-keizaireport.com

[keizaireport.com](http://www.keizaireport.com/) のRSSフィードで発生する
「同じレポートが複数のカテゴリに現れる」という重複問題を解決し、タイトル判定によってユニークな情報だけを抽出・統合するプロジェクトです。

## 特徴
- **重複排除**: 複数のフィードを横断してスキャンし、記事タイトルの類似判定によって重複記事を自動的に1つにまとめます。
- **鮮度重視**: 直近10日以内に更新があったアクティブなフィードのみを対象とすることで、古い情報のノイズを排除します。
- **自動更新**: GitHub Actionsを利用し、6時間ごとに自動で最新情報を取得・クリーンアップします。

## 公開URL
GitHub Pagesを設定することで、以下のURLからRSSフィード（XML）およびJSON形式で取得可能です。
- **RSS Feed**: `https://mash25.github.io/feed-keizaireport.com/feed.xml`
- **JSON Data**: `https://mash25.github.io/feed-keizaireport.com/index.json`

## 使い方
`data/feeds.json` に取得したいノードの情報を記載します。
```json
{
  "feed_title": "日本経済・財政",
  "url": "http://xml.keizaireport.com/rss/node_2.xml"
}
```

## 開発・運用
このプロジェクトは Python で動作しています。
- `scripts/fetch_feeds.py`: フィード取得・統合メインスクリプト
- `data/feeds.json`: 取得対象フィードリスト
