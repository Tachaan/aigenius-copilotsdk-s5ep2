# /docs

このセッションのドキュメントと手順形式のコンテンツです。

## 🐍 または #️⃣ — トラックを選択

同じアプリケーションを 2 つの言語で実装しています。どちらのトラックでも同じ Copilot
SDK の概念を学び、同じ HTTP コントラクトを公開するため、**どちらか一方だけに取り組んでください**。

| トラック | スタック | ラボ | デモ |
|:------|:------|:-----|:------|
| **.NET** | .NET 10, ASP.NET Core, Blazor WebAssembly | [labs/](labs/) | [demos/](demos/) |
| **Python** | Python 3.11+, FastAPI, static HTML + JS | [labs-python/](labs-python/) | [demos-python/](demos-python/) |

ポートは異なるため（5050/5051 と 5070）、比較したい場合は両方のスタックを同時に実行できます。

## 📚 セクション

ドキュメントは、まず**トラック別**に分類されています。.NET と Python は対等な位置づけのトラックで、
どちらにも属さない資料は Breakouts にまとめています。

| セクション | 内容 | 開始位置 |
|:--------|:-----------|:-----------|
| [**.NET — ラボ**](labs/) | Copilot SDK のハンズオン演習（全体で約 2 時間） | [ラボ 01 — セットアップ](labs/01-setup/) |
| [**.NET — デモ**](demos/) | [`src/AgentOrchestrator`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator) のコードを解説するウォークスルー | [Copilot SDK の統合](demos/01-copilot-sdk-integration.md) |
| [**Python — ラボ**](labs-python/) | Python SDK を使った同じ演習 | [ラボ 01 — セットアップ](labs-python/01-setup/) |
| [**Python — デモ**](demos-python/) | [`src/AgentOrchestrator-python`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator-python) のコードを解説するウォークスルー | [Copilot SDK の統合](demos-python/01-copilot-sdk-integration.md) |
| [**Breakouts**](breakouts/) | リファレンスと両トラック共通の Copilot CLI ラボ | [アーキテクチャ](breakouts/architecture.md) |
| [**システムマップ**](system-map/) | 実行中のシステムを示すインタラクティブな図 | [マップを開く](system-map/) |

### .NET — SDK 学習パス

| # | ラボ | 所要時間 |
|:--|:----|:-----|
| 01 | [セットアップ](labs/01-setup/) — ビルド、実行、検証 | 約 15 分 |
| 02 | [最初のチャット](labs/02-first-chat/) — SSE ストリーミングと実行時モデル | 約 20 分 |
| 03 | [ツール](labs/03-tools/) — `CopilotTool.DefineTool` | 約 20 分 |
| 04 | [イベント](labs/04-events/) — セッションイベントのライフサイクル | 約 20 分 |
| 05 | [セッション](labs/05-sessions/) — 永続化と再開 | 約 20 分 |
| 06 | [MCP](labs/06-mcp/) — MCP サーバーの接続 | 約 20 分 |
| 07 | [まとめ](labs/07-wrap-up/) — 内容の整理とクリーンアップ | 約 10 分 |

実行可能なサンプルプロジェクトは
[`src/AgentOrchestrator/samples/SdkLabs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/samples/SdkLabs) にあります。

### .NET — デモ

| # | ウォークスルー |
|:--|:------------|
| 01 | [Copilot SDK の統合](demos/01-copilot-sdk-integration.md) |
| 02 | [SSE ストリーミング](demos/02-sse-streaming.md) |
| 03 | [小売分析](demos/03-retail-analytics.md) |
| 04 | [Blazor UI](demos/04-blazor-ui.md) |

### Python — SDK 学習パス

| # | ラボ | 所要時間 |
|:--|:----|:-----|
| 01 | [セットアップ](labs-python/01-setup/) — インストール、実行、検証 | 約 15 分 |
| 02 | [最初のチャット](labs-python/02-first-chat/) — SSE ストリーミングと実行時モデル | 約 20 分 |
| 03 | [ツール](labs-python/03-tools/) — `@define_tool` | 約 20 分 |
| 04 | [イベント](labs-python/04-events/) — セッションイベントのライフサイクル | 約 20 分 |
| 05 | [セッション](labs-python/05-sessions/) — 永続化と再開 | 約 20 分 |
| 06 | [MCP](labs-python/06-mcp/) — MCP サーバーの接続 | 約 20 分 |
| 07 | [まとめ](labs-python/07-wrap-up/) — 内容の整理とクリーンアップ | 約 10 分 |

実行可能なサンプルパッケージは
[`src/AgentOrchestrator-python/sdk_labs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator-python/sdk_labs) にあります。

### Python — デモ

| # | ウォークスルー |
|:--|:------------|
| 01 | [Copilot SDK の統合](demos-python/01-copilot-sdk-integration.md) |
| 02 | [SSE ストリーミング](demos-python/02-sse-streaming.md) |
| 03 | [小売分析](demos-python/03-retail-analytics.md) |
| 04 | [Web UI](demos-python/04-web-ui.md) |

### トラック固有の追加演習

以下は任意で取り組める追加演習です。[API の拡張](labs/extra-extend-api/)は各トラックに用意されており、
SDK ではなく一般的なアプリ開発を扱います。
[.NET](labs/extra-extend-api/) · [Python](labs-python/extra-extend-api/)

### Breakouts

リファレンスと、どちらのトラックにも属さないすべての資料です。

**リファレンス** —
[アーキテクチャ](breakouts/architecture.md) ·
[カスタムエージェント](breakouts/custom-agents.md) ·
[フックとガバナンス](breakouts/hooks-and-governance.md) ·
[スキル](breakouts/skills.md) ·
[トラブルシューティング](breakouts/troubleshooting.md)

**追加ハンズオン** — 言語に依存しない Copilot **CLI** ラボです。トラックごとに重複させず、
ここにまとめています。
[カスタムエージェント](labs/extra-custom-agents/) ·
[ガバナンスフック](labs/extra-governance-hooks/)

## 🖼️ アセット

| パス | 用途 |
|:-----|:--------|
| `Slide1.png` – `Slide3.png` | セッションスライド — 「Three Mondays」のストーリー |
| `screenshots/` | README から参照される UI スクリーンショット |

## コンテンツの追加

- **ラボ** — 演習ごとに番号付きのフォルダーを 1 つ作成します（例: `07-your-topic/README.md`）。
  `labs/` は .NET トラック、`labs-python/` は Python トラックです。
- **デモ** — コードベースの領域ごとに番号付きのファイルを 1 つ作成します。
  `demos/` は .NET、`demos-python/` は Python 用です。
- **Breakouts** — リファレンストピックごとに、番号を付けずに 1 ファイルを作成します
- 画像は `screenshots/` または `assets/` サブフォルダーに配置します
- 上記の表、該当セクションの `README.md`、および [`mkdocs.yml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/mkdocs.yml)
  の `nav:` ブロックを更新します

サイトのナビゲーションはフォルダー別ではなく、**トラック別**（`.NET`、`Python`）に分類されています。
新しいページは該当するトラックの配下に追加してください。CLI の資料、リファレンス、発表者向けノートなど、
言語に依存しない内容は、ファイル自体が `labs/` や `demos/` にあっても `Breakouts` 配下に配置します。
相互リンク、`scripts/build_index.py`、リンクチェッカーがフォルダー名に依存するため、フォルダー名は変更しません。

## コンテンツのルール

- **大きなバイナリは禁止** — PowerPoint デッキ、動画、録画は配置せず、代わりにリンクを掲載します。
- **機密情報は禁止** — 顧客名、競合分析、アカウント計画、社内限定資料は含めません。
  [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md)を参照してください。
- **意図的なコードスメルを「修正」しないでください** — レビューデモ用に 4 つの問題パターンを意図的に残し、
  両トラックで同じ状態にしています。

## ライセンス

このフォルダーのドキュメントには
[CC BY 4.0](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/LICENSE-DOCS) が適用されます。`/src` のソースコードには、別途
[MIT License](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/LICENSE) が適用されます。
