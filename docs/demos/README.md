# .NET デモ

[`/src`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator) にあるコードのウォークスルーです。Agent HQ デモが*どのように*動作するかを理解するためにお読みください。[.NET ラボ](../labs/)では、対応するハンズオン演習に取り組めます。

## ウォークスルー

| # | ドキュメント | 内容 |
|:--|:----|:-------|
| 01 | [Copilot SDK の統合](01-copilot-sdk-integration.md) | `CopilotChatService` — クライアントのライフサイクル、セッションイベント、実行時のモデル検出 |
| 02 | [SSE ストリーミング](02-sse-streaming.md) | `ChatController` → ブラウザー: ワイヤ形式、フラッシュ、エラー時の入出力の契約 |
| 03 | [小売分析](03-retail-analytics.md) | ドメインモデル、EF Core、シード処理、予測、意図的なコードスメル |
| 04 | [Blazor UI](04-blazor-ui.md) | `Home.razor`、モデルピッカー、localStorage、ストリーミングレンダリング |

## 推奨する順序

このコードベースを初めて読む場合は、番号順に進めてください。各ドキュメントは、それ以前の内容を前提としています。

## ⚠️ 意図的なコードスメルについて

[ウォークスルー 03](03-retail-analytics.md) では、コードレビューのデモ用に**意図的に**残してある4つの問題のあるパターンを説明します。これらは修正対象のバグではありません。
詳しくは [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md) を参照してください。

## 関連情報

- [.NET ラボ](../labs/) — 同じ内容を扱うハンズオン演習
- [Python デモ](../demos-python/) — これらのウォークスルーに対応する FastAPI 版
- [詳細解説](../breakouts/) — アーキテクチャ図とリファレンス資料
- [アーキテクチャ](../breakouts/architecture.md) — システムの概要
