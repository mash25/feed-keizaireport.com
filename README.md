# feed-keizaireport.com

[経済レポート専門ニュース（keizaireport.com）](http://www.keizaireport.com/) の各種RSSフィードを統合・クリーンアップし、鮮度の高い情報だけをまとめた自分専用のRSSフィードを生成するプロジェクトです。

## 特徴
- **鮮度重視**: 直近10日以内に更新があったアクティブなフィードのみを対象としています。
- **自動更新**: GitHub Actionsを利用し、6時間ごとに自動で最新情報を取得・統合します。
- **重複排除**: 同じ内容のレポートが複数のフィードに含まれる場合、自動で1つにまとめます。

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
