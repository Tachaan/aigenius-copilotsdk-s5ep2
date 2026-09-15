# .NET ラボ

**GitHub Copilot SDK** に焦点を当てた、**AI Genius S5E2 — Agent HQ Demo** の
ハンズオン演習です。これは **.NET トラック**です。.NET または
[Python](../labs-python/) のどちらか**一方**を選び、順番に進めてください。
.NET は **5050/5051**、Python は **5070** を使用するため、両方のスタックを同時に実行できます。

<a id="prerequisites"></a>

## 前提条件

| 要件 | 補足 |
|:------------|:------|
| [.NET 10 SDK](https://dotnet.microsoft.com/download) | `dotnet --version` で `10.x` が表示されること |
| [GitHub Copilot CLI](https://docs.github.com/copilot) | `npm install -g @github/copilot` でインストールし、Copilot を利用できるアカウントでサインイン済みであること |
| `git`, `curl`, `jq` | `jq` はオプションのガバナンスフックラボで使用します |
| ターミナルとエディター | VS Code を推奨します。このリポジトリには `.vscode/mcp.json` が含まれています |

開始前に確認してください。

```bash
dotnet --version     # 10.x
copilot --version    # 1.x
```

## 🎯 SDK 学習パス

中心となる学習ルートです。すべて完了するまでの所要時間は約2時間です。

| # | ラボ | 内容 | 時間 |
|:--|:----|:---------------|:-----|
| 01 | [セットアップ](01-setup/) | アプリと SDK サンプルプロジェクトをビルドして実行する | 約15分 |
| 02 | [最初のチャット](02-first-chat/) | 応答をストリーミングし、実行時にモデルを検出する | 約20分 |
| 03 | [ツール](03-tools/) | `CopilotTool.DefineTool` を使ってモデルから C# を呼び出す | 約20分 |
| 04 | [イベント](04-events/) | 実際のセッションイベントのライフサイクルを確認する | 約20分 |
| 05 | [セッション](05-sessions/) | 再起動をまたいで会話を永続化し、再開する | 約20分 |
| 06 | [MCP](06-mcp/) | 自分で作成していないツールを提供する MCP サーバーを接続する | 約20分 |
| 07 | [まとめ](07-wrap-up/) | 学習内容を整理し、クリーンアップして、次のステップを選ぶ | 約10分 |

### 実行可能なサンプル

ラボ 03〜06 では、各ラボに1つのサブコマンドを割り当てた実際のコンソールプロジェクトを使用します。

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- tools
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- events
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- sessions
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- mcp
```

これらのラボに掲載しているすべてのコマンドは実際の Copilot CLI で実行し、
その出力をそのまま掲載しています。

## 📎 追加ラボ — SDK 以外

有用な内容ですが、SDK ではなく **Copilot CLI** と一般的なアプリ開発を扱います。
これらはオプションであり、番号付きの学習パスからは独立しています。

| ラボ | 扱う内容 | 追加ラボである理由 |
|:----|:-------|:---------------|
| [API の拡張](extra-extend-api/) | ASP.NET Core、EF Core、xUnit | Copilot をコーディングアシスタントとして使用し、SDK には触れないため |
| [カスタムエージェント](extra-custom-agents/) | `.agent.md` ファイル、エージェントを使ったレビュー | 両トラックで共通する Copilot CLI の機能であり、[詳細解説](../breakouts/)に分類されるため |
| [ガバナンスフック](extra-governance-hooks/) | シェルフック、セキュリティゲート、監査ログ | Copilot CLI の機能であるため。SDK で同等の内容は[ラボ 03](03-tools/)で扱います |

[API の拡張](extra-extend-api/)だけが .NET 固有です。カスタムエージェントと
ガバナンスフックは言語に依存しない CLI ラボであるため、サイトでは
[詳細解説 → 追加ハンズオン](../breakouts/)に掲載し、両トラックで同じ内容を共有しています。

## 表記規則

- コマンドはリポジトリルートから**コピーしてそのまま実行**できます
- 各手順を確認できるよう、想定される出力を掲載しています
- ⚠️ は、飛ばすと問題が生じる注意事項を示します
- 💡 は、オプションの発展課題を示します

## ⚠️ 何かを「修正」する前に

このリポジトリには、コードレビューのデモで使用する4つの問題のあるコードパターンが
**意図的に**含まれています。

- `GetTransactionsWithSegmentsAsync` の N+1 クエリ
- `GetTransactionAsync` の null チェック漏れ
- `AddTransactionAsync` の入力検証不足
- `PredictSegmentAsync` のハードコードされたしきい値

[追加 — カスタムエージェント](extra-custom-agents/)では、これらを*見つける*ことが課題です。
修正しないでください。レビュー演習は、これらが残っていることを前提としています。詳しくは
[`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md) を参照してください。

## 関連資料

- [デモ](../demos/) — これらのラボで扱うコードのウォークスルー
- [詳細解説](../breakouts/) — アーキテクチャ、エージェント、フック、トラブルシューティング
- [トラブルシューティング](../breakouts/troubleshooting.md) — 手順が失敗した場合は、まずこちらを確認してください
