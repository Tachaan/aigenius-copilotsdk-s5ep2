# システムマップ

型付き JSON ソースから生成され、外部アセットやビルド手順を必要としない、単一の
自己完結型 HTML ファイルとしてレンダリングされる小売分析アプリの対話型マップです。

2 つのトラックは機能と動作を揃えているため、1 つのマップで両方を表現します。
スタックが異なる箇所では、ノードに両方の名前（`ASP.NET Core · FastAPI`）が
表示されます。

<iframe src="map.html"
  title="Agent HQ デモ — 小売分析ランタイムアーキテクチャ"
        loading="lazy"
        style="width: 100%; height: 780px; border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px;">
</iframe>

表示領域が狭い場合は、[マップを全画面で開く ↗](map.html){target=_blank rel=noopener}

## ガイド付きビュー

マップには、目的別に構成された 3 つのビューがあります。各リンクを開くと、
それぞれの流れにフォーカスした状態で表示されます。

| ビュー | 表示内容 |
|:-----|:------|
| [チャットリクエストの経路](map.html#view=chat-request-path) | 1 つのプロンプトがブラウザーからモデルへ渡り、応答トークンがストリーミングで返されるまで |
| [モデルがデータを読み取る仕組み](map.html#view=model-data-access) | SQLite に至る読み取り専用 MCP ツールの経路 |
| [REST と永続化](map.html#view=rest-and-persistence) | アプリケーション自身の読み書きの経路 |

## 1 つのデータベースに至る 2 つの経路

注目すべき点は、`retail.db` へのアクセスに、意図的に異なる権限を持たせた
2 つの経路があることです。

- **アプリケーション**は、`RetailAnalyticsService` を介して読み書きします。
  .NET では EF Core、Python では SQLModel を使用します。
- **モデル**が SQLite に直接アクセスすることはありません。SQLite を `mode=ro` で
  開く `retail-analytics` MCP サーバー上の 5 つの読み取り専用ツールを呼び出します。
  書き込みはドライバーによって拒否されるため、プロンプトインジェクションでデータの
  変更を指示されても成功しません。

モデルに公開するツールセットがセキュリティ境界です。モデルに提供されるのは
`run_query` ではなく `get_customer_summary` であるため、任意の SQL を実行できる
抜け道を考慮する必要がありません。

## ビューアーの使用方法

| 操作 | コントロール |
|:-------|:--------|
| 図のガイドを開く | `?` |
| ノードを検索してフォーカスする | `/` |
| 2 つのノード間の経路を追跡する | `R` または **PATH** |
| コンポーネントの役割を比較する | `L` または **LENS** |
| 全体表示レーダー | `M` または **MAP** |
| ガイド付きストーリーを再生する | `P` |

ライト／ダークテーマ、パン／ズーム、PNG/SVG エクスポートは右上のメニューにあります。

## マップの再生成

型付きソースは
[`agent-hq-demo.architecture.json`](agent-hq-demo.architecture.json) です。
生成物である HTML ではなく、このファイルを編集してください。ジェネレーター CLI が
利用できる場合は、次のコマンドを実行します（[クレジット](#credits)を参照）。

```bash
node bin/archify.mjs validate architecture \
  docs/system-map/agent-hq-demo.architecture.json --quality showcase --json

node bin/archify.mjs deliver architecture \
  docs/system-map/agent-hq-demo.architecture.json \
  docs/system-map/map.html --quality showcase --json
```

`deliver` は、すべてのチェックに合格した場合にのみ `map.html` を置き換えます。
そのため、編集に問題があっても、最後に正常だったマップが維持されます。

## 関連情報

- [アーキテクチャリファレンス](../breakouts/architecture.md) — 文章による
  ウォークスルー、リクエストのシーケンス、データモデル
- [.NET ラボ 06 — MCP](../labs/06-mcp/) · [Python ラボ 06 — MCP](../labs-python/06-mcp/)
- [フックとガバナンス](../breakouts/hooks-and-governance.md) — 最小権限の仕組みを
  構成するもう一方の要素

<a id="credits"></a>

## クレジット

マップは MIT ライセンスの [Archify](https://github.com/tt-a1i/archify) で生成されています。
`map.html` にはそのビューアーランタイムが埋め込まれています。
