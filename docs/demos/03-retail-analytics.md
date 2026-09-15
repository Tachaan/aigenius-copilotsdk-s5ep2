# 小売ドメイン

このウォークスルーでは、デモで使用する小売分析のデータモデル、SQLite のセットアップ、シードデータ、REST エンドポイントについて説明します。また、コードレビューのデモ用に意図的に残してあるコードスメルも取り上げます。

## ドメインモデル

API モデルは
[`AgentHQDemo.Api/Models`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/AgentHQDemo.Api/Models)
にあります。

[`Transaction`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Models/Transaction.cs)
は1件の小売購入を表します。整数の `Id` に加え、`CustomerId`、`Amount`、`ProductCategory`、`StoreId`、`Timestamp`、`IsFlagged` を持ちます。このモデルには `Required`、`StringLength`、`Range` などの Data Annotations が含まれており、コントローラーが `ModelState` を確認するときに ASP.NET Core のモデルバインディングで利用できます。

[`CustomerSegment`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Models/CustomerSegment.cs)
は分析セグメントを表します。セグメント名、説明、顧客数、月間平均支出、継続率を保持します。

[`SegmentPrediction`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Models/SegmentPrediction.cs)
は予測呼び出しから返される不変のレコードです。顧客 ID、予測セグメント、信頼度スコア、主要な特徴量名を含みます。

## データベースと起動時のシード処理

[`RetailDbContext`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Data/RetailDbContext.cs)
は、2つのセットを持つ小規模な EF Core コンテキストです。

```csharp
public DbSet<Transaction> Transactions => Set<Transaction>();
public DbSet<CustomerSegment> Segments => Set<CustomerSegment>();
```

[`Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs)
では、`Data Source=retail.db` で SQLite を構成し、`RetailAnalyticsService` を登録して、アプリケーションの起動時にデータをシードします。

```csharp
await db.Database.EnsureCreatedAsync();
await service.SeedDataAsync();
```

`RetailAnalyticsService.SeedDataAsync` は、通常のデモ再起動に対して冪等です。トランザクションが1件でも存在する場合は、すぐに処理を終了します。新しいデータベースでは、サンプルのトランザクションとセグメントを挿入して変更を保存します。

## シードデータ

シードには、顧客 `C001` から `C005` までの10件のトランザクションが含まれます。

| 顧客 | シードされた購入パターン |
| --- | --- |
| `C001` | Grocery と Electronics の購入、合計 335.49 |
| `C002` | Grocery と Health の購入、合計 47.50 |
| `C003` | Electronics と Fashion の購入、合計 1,700.00 |
| `C004` | 少額の Grocery 購入2件、合計 21.49 |
| `C005` | Electronics と Fashion の購入、合計 995.00 |

さらに、4つの顧客セグメントを作成します。

| セグメント | 顧客数 | 月間平均支出 | 継続率 | 説明 |
| --- | ---: | ---: | ---: | --- |
| High Value | 150 | $850 | 92% | ロイヤルティ指標が高い、支出額上位10%の顧客 |
| Regular | 3,200 | $180 | 78% | 複数カテゴリで毎月継続的に購入する顧客 |
| At Risk | 890 | $95 | 45% | 過去90日間で購入頻度が低下している顧客 |
| New | 420 | $120 | 65% | 過去90日以内に加わった顧客 |

## REST エンドポイント

[`TransactionsController`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/TransactionsController.cs)
は、トランザクションの読み取り、作成、削除を行うエンドポイントを公開します。

| エンドポイント | 戻り値 |
| --- | --- |
| `GET /api/transactions` | すべての `Transaction` レコード。 |
| `GET /api/transactions/{id}` | 1件の `Transaction`。コントローラーが `null` を受け取った場合は `404`。 |
| `POST /api/transactions` | トランザクションを作成し、保存したレコードとともに `201 Created` を返す。 |
| `DELETE /api/transactions/{id}` | 削除時は `204 No Content`、見つからない場合は `404`。 |

[`SegmentsController`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/SegmentsController.cs)
は、セグメントと予測のエンドポイントを公開します。

| エンドポイント | 戻り値 |
| --- | --- |
| `GET /api/segments` | すべての `CustomerSegment` レコード。 |
| `GET /api/segments/{id}` | 1件の `CustomerSegment`。見つからない場合は `404`。 |
| `GET /api/segments/predict/{customerId}` | その顧客の `SegmentPrediction`。 |

チャットエンドポイントは、小売データ API ではなく Copilot のストリーミング経路に含まれるため、[SSE による応答のストリーミング](./02-sse-streaming.md)で説明します。

## セグメント予測ロジック

[`RetailAnalyticsService.PredictSegmentAsync`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/RetailAnalyticsService.cs)
は、顧客の全トランザクションを読み込み、総支出、平均支出、購入頻度を算出します。その後、次のルールを順番に適用します。

1. トランザクションなし: 信頼度 `0.5`、`no_history` とともに `New` を返す。
2. 総支出が `1000` を超える: 信頼度 `0.89` で `High Value` を返す。
3. 購入頻度が3回以上: 信頼度 `0.75` で `Regular` を返す。
4. 平均支出が `50` 未満: 信頼度 `0.62` で `At Risk` を返す。
5. それ以外: 信頼度 `0.55` で `Regular` を返す。

返される `TopFeatures` 配列は、総支出、頻度、平均支出など、ルールへの入力を示します。

## 意図的な4つのコードスメル

これらはコードレビューセッション用に意図的に用意したデモ素材です。このデモ中に修正すべき偶発的なバグとして扱わず、レビュー担当者が気付き、説明すべき例として使用してください。

### 1. `RetailAnalyticsService.GetTransactionsWithSegmentsAsync` の N+1 クエリ

**内容:** このメソッドはすべてのトランザクションを読み込んだ後、各トランザクションをループし、その顧客に対する別のデータベースクエリを実行する `PredictSegmentAsync` を呼び出します。

**問題となる理由:** クエリ数がトランザクション数に比例して増加します。少量のシードデータでは許容できますが、実際の小売データ量では処理が遅くなり、コストも高くなる可能性があります。

**レビューで指摘すべき内容:** 「これは N+1 クエリパターンです。顧客のトランザクションデータを一括取得するか、リクエストですでに読み込んだデータからセグメント予測を計算することを検討してください。」

### 2. `RetailAnalyticsService.GetTransactionAsync` の null チェック不足

**内容:** サービスは `FindAsync(id)` を使用し、`!` で null 許容フローを抑制して、データベースから行が返されない可能性があるにもかかわらず `Task<Transaction>` を返します。

**問題となる理由:** 呼び出し元は、シグネチャから `null` の可能性を判断できません。また、今後追加されるコードが確認前に `null` のメンバーにアクセスする可能性があります。

**レビューで指摘すべき内容:** 「サービスの入出力の契約は、`Transaction?` や結果型を返すなどして未検出のケースを表現し、呼び出し元で明示的に処理する必要があります。」

### 3. `RetailAnalyticsService.AddTransactionAsync` の入力検証不足

**内容:** サービスは渡された `Transaction` を受け取り、`Timestamp = DateTime.UtcNow` を設定し、金額、顧客 ID、カテゴリ、店舗の値を確認せずに保存します。

**問題となる理由:** `TransactionsController.Create` は `ModelState` を確認しますが、サービス自体はテスト、他のサービス、将来のエンドポイントから直接呼び出せます。その場合、不正なドメインデータがコントローラーの検証を迂回する可能性があります。

**レビューで指摘すべき内容:** 「ドメインの不変条件について、コントローラーの検証だけに依存しないでください。サービス内でトランザクションを検証するか、ルールを一元化し、すべての呼び出し元に同じ保護を適用してください。」

### 4. `RetailAnalyticsService.PredictSegmentAsync` のハードコードされたしきい値

**内容:** High Value のルールで、リテラル値 `1000` をしきい値として使用しています。

**問題となる理由:** ビジネス上のしきい値は、市場、季節、小売業者によって変わります。コード内に隠れたマジックナンバーは、監査、調整、ビジネス関係者への説明が困難です。

**レビューで指摘すべき内容:** 「High Value のしきい値を構成またはポリシーオブジェクトへ移し、明確な名前を付け、境界での動作をテストしてください。」

## 関連情報

- [Copilot SDK の組み込み](./01-copilot-sdk-integration.md)
- [SSE による応答のストリーミング](./02-sse-streaming.md)
- [Blazor フロントエンド](./04-blazor-ui.md)
- ソース:
  [`RetailAnalyticsService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/RetailAnalyticsService.cs),
  [`RetailDbContext.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Data/RetailDbContext.cs),
  [`Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs),
  [`Models`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/AgentHQDemo.Api/Models),
  [`TransactionsController.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/TransactionsController.cs),
  [`SegmentsController.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/SegmentsController.cs)
