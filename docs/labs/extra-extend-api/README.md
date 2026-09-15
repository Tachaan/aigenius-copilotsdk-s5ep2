# 追加ラボ — API の拡張

> **📎 追加ラボ — Copilot SDK の内容ではありません。**
> ここではデモアプリの ASP.NET Core、EF Core、xUnit を扱います。Copilot を
> *コーディングアシスタント*として使用しますが、Copilot SDK には触れません。
> オプションであり、番号付きの SDK 学習手順からは独立しています。

**目標:** 意図的なコードスメルを残し、既存の 26 テストを成功させたまま、Copilot を使用して
新しいエンドポイントとテストを追加します。

**所要時間:** 約 30 分

**前提条件:** [Extra — ガバナンスフック](../extra-governance-hooks/) を完了し、両方の
サービスを実行できること。

## ⚠️ 基本ルール

1. **意図的な 4 つのコードスメルを修正しないでください。** 後続のデモがこれらに依存します。
    Copilot が `GetTransactionsWithSegmentsAsync` の改善を提案しても断ってください。
2. **既存の 14 テストをすべて成功させてください。** 新しいテストはこの数に追加されます。
3. 次のファイルの規約に従ってください。
   [`copilot-instructions.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-instructions.md) —
    ファイルスコープ名前空間、プライマリコンストラクター、`async`/`Async` サフィックス、
    `CancellationToken`、`record` DTO。

## 構築するもの

`GET /api/segments/summary` — 全セグメントにわたるポートフォリオレベルの統計:

```json
{
  "totalSegments": 4,
  "totalCustomers": 4660,
  "weightedAverageRetention": 0.71,
  "highestRetention": "High Value",
  "lowestRetention": "At Risk"
}
```

意図的に単純なパススルーにはしていません。加重平均では顧客数によって顧客維持率を重み付けする
必要があり、まさにテストする価値がある処理です。

## 手順 1 — 既存の構造を確認する

```bash
cat src/AgentOrchestrator/AgentHQDemo.Api/Controllers/SegmentsController.cs
```

踏襲すべきパターンを確認します。

- プライマリコンストラクターによる注入: `SegmentsController(RetailAnalyticsService service)`
- `[HttpGet("{id:int}")]` のルート制約
- `ActionResult<T>` を返し、リソースがない場合は `NotFound()` を返す
- Controller は薄く保ち、ロジックは service に置く

## 手順 2 — テストの書き方を確認する

```bash
cat src/AgentOrchestrator/tests/AgentHQDemo.Tests/RetailAnalyticsServiceTests.cs
```

このテストクラスは **in-memory SQLite** コンテキストを構築します。

```csharp
var options = new DbContextOptionsBuilder<RetailDbContext>()
    .UseSqlite("DataSource=:memory:")
    .Options;

_db = new RetailDbContext(options);
_db.Database.OpenConnection();
_db.Database.EnsureCreated();
```

`OpenConnection()` の呼び出しは重要です。in-memory SQLite データベースは、接続が開いている
間だけ存在します。接続を閉じると、テストの途中でスキーマが消えます。

## 手順 3 — DTO を追加する

`src/AgentOrchestrator/AgentHQDemo.Api/Models/SegmentSummary.cs` を作成します。

```csharp
namespace AgentHQDemo.Api.Models;

/// <summary>
/// Portfolio-level statistics across all customer segments.
/// </summary>
public record SegmentSummary(
    int TotalSegments,
    int TotalCustomers,
    decimal WeightedAverageRetention,
    string HighestRetention,
    string LowestRetention);
```

不変 DTO であり、このリポジトリのスタイルに合わせて `record` を使用します。

## 手順 4 — service メソッドを追加する

最初に制約を示して Copilot に依頼します。

```
Add a GetSegmentSummaryAsync method to RetailAnalyticsService that returns a
SegmentSummary. Weight the average retention by CustomerCount, not a plain
mean. Handle the empty-segment case without throwing. Accept an optional
CancellationToken and pass it to async EF Core calls. Follow the existing
conventions in this file. Do not modify any other method.
```

目標とする実装は次のとおりです。

```csharp
public async Task<SegmentSummary> GetSegmentSummaryAsync(
    CancellationToken cancellationToken = default)
{
    var segments = await _db.Segments.ToListAsync(cancellationToken);

    if (segments.Count == 0)
        return new SegmentSummary(0, 0, 0m, string.Empty, string.Empty);

    var totalCustomers = segments.Sum(s => s.CustomerCount);
    var weighted = totalCustomers == 0
        ? 0m
        : segments.Sum(s => s.RetentionRate * s.CustomerCount) / totalCustomers;

    return new SegmentSummary(
        segments.Count,
        totalCustomers,
        Math.Round(weighted, 2),
        segments.OrderByDescending(s => s.RetentionRate).First().Name,
        segments.OrderBy(s => s.RetentionRate).First().Name);
}
```

⚠️ **ゼロ除算を防いでください。** `totalCustomers` が 0 の場合は例外が発生します。シードを
使用すれば空のテーブルはほぼありませんが、テストでは作成できます。レビュアーも確認する点です。

## 手順 5 — エンドポイントを追加する

`SegmentsController` に次を追加します。

```csharp
[HttpGet("summary")]
public async Task<ActionResult<SegmentSummary>> GetSummary(
    CancellationToken cancellationToken)
{
    return Ok(await service.GetSegmentSummaryAsync(cancellationToken));
}
```

⚠️ **ルートの順序。** `summary` が別のルートに取り込まれないようにする必要があります。ここでは
隣接するルートが `{id:int}` に制約されているため安全です。単なる `{id}` だった場合、
`/api/segments/summary` は "summary" を id としてバインドしようとして失敗します。不明な場合は
ルートの優先順位について Copilot に確認してください。

## 手順 6 — テストを作成する

```
Add xUnit tests to RetailAnalyticsServiceTests for GetSegmentSummaryAsync.
Cover: the seeded four-segment case, correct weighted average (not a plain
mean), and an empty database returning zeros without throwing. Follow the
existing in-memory SQLite setup in this class. Remember that the constructor
starts with an empty database, so seed the seeded-case tests explicitly.
```

顧客維持率の加重平均のケースは特に注意が必要です。シードデータは次のとおりです。

| セグメント | 顧客数 | 顧客維持率 |
|:--------|----------:|----------:|
| High Value | 150 | 0.92 |
| Regular | 3,200 | 0.78 |
| At Risk | 890 | 0.45 |
| New | 420 | 0.65 |

単純平均は `0.70` です。加重平均は
`(150×0.92 + 3200×0.78 + 890×0.45 + 420×0.65) / 4660 ≈ 0.71`
となり、値が異なります。これこそテストを作成する価値がある理由です。加重値をアサートすれば、
単純な実装は明確に失敗します。

```csharp
[Fact]
public async Task GetSegmentSummaryAsync_WeightsRetentionByCustomerCount()
{
    await _service.SeedDataAsync();

    var summary = await _service.GetSegmentSummaryAsync();

    Assert.Equal(4, summary.TotalSegments);
    Assert.Equal(4660, summary.TotalCustomers);
    Assert.Equal("High Value", summary.HighestRetention);
    Assert.Equal("At Risk", summary.LowestRetention);
    Assert.Equal(0.71m, summary.WeightedAverageRetention);
    Assert.NotEqual(0.70m, summary.WeightedAverageRetention);
}
```

💡 in-memory データベースは空の状態で開始します。4 つのサンプルセグメントを検証するテストでは
シードし、セグメントが 0 のケースでは空のままにします。

## 手順 7 — ビルドしてテストする

```bash
dotnet build src/AgentOrchestrator/AgentHQDemo.slnx
dotnet test  src/AgentOrchestrator/AgentHQDemo.slnx
```

想定結果は、警告のないビルドと、失敗なしで **14 件を超える**テストの成功です。

⚠️ 以前成功していたテストが失敗する場合は、新しいコード以外の何かが変更されています。
差分を確認してください。

```bash
git diff --stat
```

表示されるのは `SegmentSummary.cs`、`RetailAnalyticsService.cs`、`SegmentsController.cs`、
テストファイルだけである必要があります。

## 手順 8 — 実際に動かして確認する

```bash
dotnet run --project src/AgentOrchestrator/AgentHQDemo.Api --urls "http://localhost:5050"
```

```bash
curl -s http://localhost:5050/api/segments/summary | jq
```

数値が上の表と一致し、既存のエンドポイントも引き続き動作することを確認します。

```bash
curl -s http://localhost:5050/api/segments | jq 'length'          # 4
curl -s http://localhost:5050/api/segments/predict/C003 | jq -r .predictedSegment
```

## 手順 9 — 自分の変更をレビューする

ラボ 03 のエージェントを使用して仕上げます。

```bash
copilot --agent dotnet-reviewer -p "Review my uncommitted changes for correctness, async usage, and adherence to .github/copilot-instructions.md. Report only." --allow-all-tools
```

次に、ルートの [`README.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/README.md) にある API の表を更新し、
新しいエンドポイントを追加します。ドキュメントの乖離もレビューで指摘すべき問題です。

## ✅ チェックポイント

- [x] 新しい `record` DTO、service メソッド、エンドポイントを追加した
- [x] 加重平均と空のケースをテストでカバーした
- [x] 元の 26 テストがすべて引き続き成功する
- [x] 意図的な 4 つのコードスメルを変更していない
- [x] 実行中の API に対してエンドポイントを検証した

## 💡 発展課題

`GET /api/transactions/summary` を追加し、商品カテゴリおよび店舗別の合計を返します。
`GetTransactionsWithSegmentsAsync` の N+1 パターンが入り込まないか検討し、発生しないように
実装してください。

## 関連項目

- 次へ: [ラボ 07 — まとめ](../07-wrap-up/)
- [デモ: 小売分析](../../demos/03-retail-analytics.md)
- [補足資料: アーキテクチャ](../../breakouts/architecture.md)
