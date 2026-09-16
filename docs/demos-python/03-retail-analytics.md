# 小売ドメイン

このウォークスルーでは、Python 版小売分析アプリのデータモデル、SQLite の設定、初期データ、REST エンドポイント、検証時の動作、そしてデモ用に意図的に残してあるコードスメルを説明します。

## ドメインモデル

API モデルは [`app/models.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/models.py) にあります。永続化には SQLModel を、リクエストとレスポンスの検証には Pydantic を使っています。

`TransactionBase` には、制約付きのリテール購買フィールドが含まれています。

```python
class TransactionBase(SQLModel):
    """Validated fields for a retail purchase transaction."""

    model_config = CAMEL_CONFIG

    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0.01, le=1_000_000)
    product_category: str = Field(min_length=1, max_length=50)
    store_id: str = Field(min_length=1, max_length=50)
```

`Transaction` は `id`、`timestamp`、`is_flagged` を持つテーブルモデルです。`CustomerSegment` はセグメントのメタデータを保持します。`SegmentPrediction` は `customerId`、`predictedSegment`、`confidence`、`topFeatures` を返します。

## CamelCase JSON とバリデーション

Python モデルは内部では snake_case を維持しつつ、通信時には camelCase にシリアライズされるため、.NET の契約を意図的に保っています。

```python
#: Serialize as camelCase but still accept snake_case when constructing in Python.
CAMEL_CONFIG = ConfigDict(alias_generator=to_camel, populate_by_name=True)
```

そのため、API の JSON では `customerId`、`productCategory`、`isFlagged` が使われます。

⚠️ SQLModel は `table=True` のクラスでは検証を実行しません。そのため、制約付きフィールドは `TransactionBase` に置かれ、`Transaction` と `TransactionCreate` の両方がそれを継承しています。FastAPI はルーターがサービスを呼ぶ前に `TransactionCreate` を検証し、不正なリクエスト本文に対して HTTP 422 を返します。

```python
class TransactionCreate(TransactionBase):
    """Request body for creating a transaction.

    FastAPI validates this automatically and returns HTTP 422 on failure, which
    is what ``ModelState.IsValid`` does in the .NET ``TransactionsController``.
    """
```

## データベースと起動時の初期データ投入

[`app/database.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/database.py) は、SQLite エンジンと、リクエストごとのセッション依存関係を作成します。

```python
DATABASE_URL = "sqlite:///retail.db"

engine = create_engine(DATABASE_URL, echo=False)
```

[`app/main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py) は、FastAPI のライフスパンハンドラー内で初期データを投入します。

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed database on startup
    create_db_and_tables()
    with Session(engine) as session:
        await RetailAnalyticsService(session).seed_data()
```

取引データがすでに存在する場合、初期データ投入メソッドはすぐに処理を終えるため、デモを何度再起動しても同じ状態になります。

## 初期データ

このテストデータには、顧客 `C001` から `C005` にまたがる 10 件の取引が含まれています。

| 顧客 | 投入される購入パターン |
| --- | --- |
| `C001` | Grocery と Electronics の購買が合計 335.49 |
| `C002` | Grocery と Health の購買が合計 47.50 |
| `C003` | Electronics と Fashion の購買が合計 1,700.00 |
| `C004` | 少額の Grocery 購買 2 件で合計 21.49 |
| `C005` | Electronics と Fashion の購買が合計 995.00 |

あわせて、High Value、Regular、At Risk、New の 4 つの顧客セグメントも作成されます。

## REST エンドポイント

[`app/routers/transactions.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/transactions.py) は、取引の取得、作成、削除を行う各エンドポイントを公開しています。

| エンドポイント | 戻り値 |
| --- | --- |
| `GET /api/transactions` | すべての `Transaction` レコード。 |
| `GET /api/transactions/{id}` | 1 件の `Transaction`。見つからない場合は `404`。 |
| `POST /api/transactions` | 取引を作成し、保存済みレコードとともに `201 Created` を返します。 |
| `DELETE /api/transactions/{id}` | 削除時は `204 No Content`、見つからない場合は `404`。 |

[`app/routers/segments.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/segments.py) は、`GET /api/segments`、`GET /api/segments/{segment_id}`、`GET /api/segments/predict/{customer_id}` を公開しています。

チャットエンドポイントは、リテールデータ API ではなく Copilot のストリーミング経路に属するため、[SSE によるストリーミング応答](./02-sse-streaming.md) で扱っています。

## セグメント予測のロジック

[`RetailAnalyticsService.predict_segment`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py) は、ある顧客の全取引を読み込み、総支出、平均支出、購買頻度を算出します。そのうえで、次のルールをこの順番で適用します。

1. 取引がない場合: 信頼度 `0.5` と `no_history` を添えて `New` を返します。
2. 総支出が `1000` を超える場合: 信頼度 `0.89` で `High Value` を返します。
3. 頻度が 3 回以上の場合: 信頼度 `0.75` で `Regular` を返します。
4. 平均支出が `50` 未満の場合: 信頼度 `0.62` で `At Risk` を返します。
5. それ以外: 信頼度 `0.55` で `Regular` を返します。

返される `topFeatures` 配列は、総支出、頻度、平均支出など、どのルール入力が効いたかを説明します。

## curl で試す

実際に確認した出力は次のとおりです。

```bash
$ curl http://localhost:5070/api/segments/predict/C003
{"customerId":"C003","predictedSegment":"High Value","confidence":0.89,"topFeatures":["high_total_spend","multi_category","total_1700"]}

$ curl http://localhost:5070/api/segments/predict/C999
{"customerId":"C999","predictedSegment":"New","confidence":0.5,"topFeatures":["no_history"]}

$ curl http://localhost:5070/api/transactions/1
{"productCategory":"Grocery","customerId":"C001","amount":245.5,"isFlagged":false,"storeId":"S001","id":1,"timestamp":"2026-07-14T03:58:08.543810"}
```

`GET /api/transactions` は 10 行を返します。`GET /api/segments` は 4 行を返します。`GET /api/transactions/999` は HTTP 404 を返します。

## テスト

pytest スイートは .NET の xUnit テストと対応しており、さらにブラウザーと API 間のリクエスト形式を守る Python 専用のコントラクトテストが 4 本あります。実際に確認したテスト結果は次のとおりです。

```bash
$ uv run pytest
18 passed
```

## 意図的に残してある 4 つのコードスメル

これらはコードレビュー セッション用に意図的に用意されたデモ素材です。このデモの中で、うっかり入ったバグとして修正対象にしないでください。レビュアーが気づき、説明すべきポイントの例として使います。.NET 版と対応しているため、同じ解答例を使えます。

### 1. `get_transactions_with_segments` の N+1 クエリ

**内容:** このメソッドは全取引を読み込んだ後、各取引を順に処理して `predict_segment` を呼び出します。これにより、その顧客に対する追加のデータベースクエリが実行されます。

```python
for txn in transactions:
    # N+1: querying segments for every single transaction
    segment = await self.predict_segment(txn.customer_id)
```

**問題となる理由:** クエリ数が取引件数に応じて増加します。レビュアーは、顧客の取引データをまとめて処理するか、そのリクエストのためにすでに読み込んだデータから予測を計算するよう提案すべきです。

### 2. `get_transaction` の `None` チェック不足

**内容:** データベースが行を返さない可能性があるにもかかわらず、サービスは `self._db.get(...)` の結果をそのまま返しています。

```python
# Missing null check: will return None if not found
return self._db.get(Transaction, transaction_id)
```

**問題となる理由:** 呼び出し側は、シグネチャから `None` があり得ることを判断できません。レビュアーは、`Transaction | None` もしくは結果型を要求し、呼び出し側で明示的に処理させるべきです。

### 3. `add_transaction` の入力検証不足

**内容:** このサービスは渡された `Transaction` を受け取り、タイムスタンプを付与して、金額、顧客 ID、カテゴリー、店舗の値を確認せずに保存します。

```python
# No validation: negative amounts and empty customer_id are allowed
transaction.timestamp = datetime.now(UTC)
self._db.add(transaction)
```

**問題となる理由:** FastAPI は `TransactionCreate` を検証しますが、テスト、他のサービス、将来のエンドポイントがこのサービスを直接呼ぶ可能性があります。レビュアーは、ドメインの不変条件をサービスかポリシーに集約するよう提案すべきです。

### 4. `predict_segment` のハードコードされた閾値

**内容:** high-value ルールが、コード中でリテラルの閾値 `1000` を使っています。

```python
# BUG: Hardcoded magic number — should be configurable
if total_spend > 1000:
```

**問題となる理由:** 閾値は市場、季節、小売業者によって変わります。レビュアーは、この閾値を設定値または名前付きのポリシーオブジェクトに移し、境界値の挙動をテストでカバーするよう求めるべきです。

## 関連項目

- [Copilot SDK の組み込み](./01-copilot-sdk-integration.md)
- [SSE によるストリーミング応答](./02-sse-streaming.md)
- [ブラウザー UI](./04-web-ui.md)
- ソース: [`retail_analytics.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py), [`models.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/models.py), [`database.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/database.py), [`main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py), [`transactions.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/transactions.py), [`segments.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/segments.py), [`conftest.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/conftest.py), [`test_retail_analytics.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_retail_analytics.py), [`test_transaction_validation.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_transaction_validation.py)
