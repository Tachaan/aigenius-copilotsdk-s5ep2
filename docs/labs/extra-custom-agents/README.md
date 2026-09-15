# 追加ラボ — カスタムエージェントとコードレビュー

> **📎 追加ラボ — Copilot SDK の内容ではありません。**
> ここでは Copilot SDK ではなく、**Copilot CLI** の機能である `.agent.md` ファイルを扱います。
> 実用的な内容ですが、オプションであり、番号付きの SDK 学習手順からは独立しています。
> SDK を学ぶ場合は [ラボ 01](../01-setup/) から開始してください。

**目標:** リポジトリのカスタムエージェントを使用して、意図的に残された 4 つのコードスメルを
検出し、エージェント、instructions、skills を組み合わせてチームのレビュー基準を
定義する方法を理解します。

**所要時間:** 約 20 分

**前提条件:** [ラボ 02](../02-first-chat/) を完了していること。GitHub Copilot CLI に
サインインしているか、Copilot Chat を備えた VS Code が必要です。

## ⚠️ 最初にお読みください

これから検出する問題は**意図的**に残されています。レビューで実際に検出できる対象を用意する
ためです。**修正しないでください**。ラボ 05 と review-instructions ファイルは、これらが
残っていることを前提としています。

ここで行うのは*検出と説明*であり、修正ではありません。

## 手順 1 — チェックインされている内容を確認する

```bash
ls .github/agents/
cat .github/agents/dotnet-reviewer.agent.md
```

各エージェントは YAML frontmatter を含む Markdown ファイルです。

```yaml
---
name: dotnet-reviewer
description: Senior .NET code reviewer specializing in C# best practices, security, and performance
tools: ['agent', 'read', 'search']
model: claude-sonnet-4.6
---
```

- **`name`** — 呼び出し時に使用する名前
- **`description`** — このエージェントを使用する*タイミング*を Copilot に伝える
- **`tools`** — 使用を許可する機能。これらは read-only のレビュアーなので、`edit` や
  `bash` は含まれない
- **`model`** — 必要に応じて特定のモデルを固定する

ここには 4 つのエージェントが含まれています。

| エージェント | 目的 |
|:------|:--------|
| `dotnet-reviewer` | C# のベストプラクティス、セキュリティ、パフォーマンス |
| `security-scanner` | 脆弱性とコンプライアンスの問題 |
| `pr-summary` | 差分から PR の説明を生成 |
| `accessibility-auditor` | UI コードの WCAG 準拠 |

## 手順 2 — 共有コンテキストを理解する

エージェントは単独で動作するわけではありません。2 つの instruction ファイルがリポジトリ
全体に適用されます。

```bash
head -40 .github/copilot-instructions.md
head -30 .github/copilot-review-instructions.md
```

- [`copilot-instructions.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-instructions.md) —
  すべてのエージェントが従うコーディング規約（ファイルスコープ名前空間、非同期処理の規約、
  例外より `Result<T>` を優先することなど）
- [`copilot-review-instructions.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-review-instructions.md) —
  レビュー固有のコンテキスト。SDK 名前空間の移動、SSE の flush 要件、意図的なコードスメルの
  明示的な一覧を含み、レビュアーが新しいバグとして報告しないようにする

この階層化が重要です。規約をバージョン管理に格納することで、人間でもエージェントでも、
すべてのレビュアーが同じ規約を適用します。

## 手順 3 — エージェントでサービスをレビューする

問題の大半を含むファイルに対して .NET レビュアーを実行します。

```bash
copilot --agent dotnet-reviewer -p "Review src/AgentOrchestrator/AgentHQDemo.Api/Services/RetailAnalyticsService.cs for performance and correctness issues. List each with severity and a suggested fix, but do not modify any files." --allow-all-tools
```

VS Code Copilot Chat では、同等の操作は次のとおりです。

```
@dotnet-reviewer review RetailAnalyticsService.cs for performance and correctness issues
```

## 手順 4 — 検出結果を解答と照合する

適切なレビューでは 4 つすべてが検出されます。解答は次のとおりです。

| # | 問題 | 場所 | 重要な理由 |
|:--|:------|:------|:---------------|
| 1 | **N+1 クエリ** | `GetTransactionsWithSegmentsAsync` | 全トランザクションを読み込んだ後、行ごとに `PredictSegmentAsync` を呼び出すため、毎回余分な往復が発生します。シードデータ 10 行なら問題になりませんが、1,000 万行では致命的です。 |
| 2 | **null チェックの欠落** | `GetTransactionAsync` | 存在しない id を考慮せずに返すため、呼び出し元が `null` のメンバーにアクセスする可能性があります。 |
| 3 | **入力検証なし** | `AddTransactionAsync` | 検証されていない入力を受け入れるため、負の金額、空の顧客 id、異常な値がすべて永続化されます。 |
| 4 | **しきい値のハードコード** | `PredictSegmentAsync` | マジックナンバーでセグメント所属を決定しています。ビジネスルールの変更に再デプロイが必要です。 |

N+1 はソースから直接確認でき、コメントでも明示されています。

```csharp
foreach (var txn in transactions)
{
    // N+1: querying segments for every single transaction
    var segment = await PredictSegmentAsync(txn.CustomerId);
    ...
}
```

💡 エージェントはいくつ検出しましたか？エージェントの動作には確率的な要素があるため、
1 回の実行で 4 つ中 3 つを検出するのは通常の結果です。ここから得られる重要な教訓は、
エージェントはレビューを高速化しますが、レビュアーの代わりにはならないということです。

## 手順 5 — security scanner へ連携する

エージェントが異なれば観点も異なります。security scanner は問題 3 に注目するはずです。

```bash
copilot --agent security-scanner -p "Scan src/AgentOrchestrator/AgentHQDemo.Api/Controllers/TransactionsController.cs and the service it calls for input validation and injection risks. Report findings only, make no edits." --allow-all-tools
```

2 つの出力を比較してください。.NET reviewer はパフォーマンスを重視し、security scanner は
信頼境界を重視します。同じコードでも優先事項が異なります。これこそ、1 つの汎用エージェント
ではなく、別々のエージェントにする理由です。

## 手順 6 — UI のアクセシビリティを監査する

```bash
copilot --agent accessibility-auditor -p "Audit src/AgentOrchestrator/AgentHQDemo.Web/Components/ChatInput.razor and Header.razor for WCAG issues. Report only." --allow-all-tools
```

ラベルの関連付け、キーボード操作性、ストリーミングメッセージ領域のフォーカス管理を確認します。

## 手順 7 — PR の概要を生成する

未コミットの変更がある状態で、`pr-summary` に説明の下書きを作成させます。

```bash
copilot --agent pr-summary -p "Summarise the current git diff as a pull request description." --allow-all-tools
```

## ✅ チェックポイント

- [x] `.agent.md` の frontmatter フィールドを説明できる
- [x] 意図的な 4 つの問題を検出し、**そのまま残した**
- [x] 2 つのエージェントが同じコードについて異なる結論を出すことを確認した
- [x] instruction ファイルがすべてのエージェントに共通規約を与える仕組みを理解した

## 💡 発展課題

5 つ目のエージェントを作成します。起動すべきタイミングを説明する `description` と
`tools: ['read', 'search']` を指定した `.github/agents/test-writer.agent.md` を作成します。
`PredictSegmentAsync` のテストを作成するのではなく、提案するよう依頼してください。

## 関連項目

- 次へ: [Extra — ガバナンスフック](../extra-governance-hooks/)
- [補足資料: カスタムエージェント](../../breakouts/custom-agents.md)
- [補足資料: Skills](../../breakouts/skills.md)
- [デモ: 小売分析](../../demos/03-retail-analytics.md)
