# Python デモ

以下は、
[`src/AgentOrchestrator-python/README.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md)
で紹介している Python コードのウォークスルーです。FastAPI 版 Agent HQ デモが*どのように*
動作するかを理解するためにお読みください。[Python ラボ](../labs-python/)では、対応する内容を実際に操作しながら学べます。

## 発表用カンペ

[Python デモ発表カンペ](presenter-notes.md)では、完成形からストリーミング、モデル選択、
ツール呼び出し、アーキテクチャ、ガバナンスへ進む 40 分の流れを、画面操作・コード行番号・セリフ付きで紹介します。
イベントとツールのラボ実演、事前準備、30・15・10 分版への短縮方法、トラブル時の進行も含みます。

## ウォークスルー

| # | ドキュメント | 内容 |
|:--|:----|:-------|
| 01 | [Copilot SDK の統合](01-copilot-sdk-integration.md) | `CopilotChatService` — クライアントのライフサイクル、セッションイベント、コールバックからキューへのストリーミング、実行時のモデル検出 |
| 02 | [SSE ストリーミング](02-sse-streaming.md) | `app.routers.chat` → ブラウザー: 通信形式、`StreamingResponse`、エラー処理の契約 |
| 03 | [小売分析](03-retail-analytics.md) | SQLModel モデル、SQLite、初期データの投入、予測、検証、意図的なコードスメル |
| 04 | [Web UI](04-web-ui.md) | 静的 HTML、Vanilla JavaScript、モデルピッカー、localStorage、ストリーミング描画 |

## 推奨順序

Python スタックを初めて使用する場合は、番号順に読んでください。各ページは前のページの内容を前提としています。
.NET トラックをすでに理解している場合は、SDK 統合ページから始め、Python と .NET の違いを中心に確認してください。

## ⚠️ 意図的なコードスメルについて

[ウォークスルー 03](03-retail-analytics.md) では、コードレビューのデモ用に**意図的に**含めた
4 つの問題のあるパターンを説明します。これらは修正対象のバグではありません。
Python サービスは .NET サービスと同じ構成のため、同じ解答例を使用できます。

## 関連情報

- [.NET デモ](../demos/) — Blazor + ASP.NET Core を使用した元のウォークスルー
- [Python ラボ](../labs-python/) — 同じ内容を扱うハンズオン演習
- [詳細解説](../breakouts/) — アーキテクチャ図とリファレンス資料
- [アーキテクチャ](../breakouts/architecture.md) — システムの概要
