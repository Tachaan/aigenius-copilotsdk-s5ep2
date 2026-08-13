# The retail domain

This walkthrough documents the Python retail analytics data model, SQLite setup, seed data, REST endpoints, validation behaviour, and deliberate code smells used by the demo.

## Domain models

The API models live in [`app/models.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/models.py). They use SQLModel for persistence and Pydantic for request/response validation.

`TransactionBase` contains the constrained retail purchase fields:

```python
class TransactionBase(SQLModel):
    """Validated fields for a retail purchase transaction."""

    model_config = CAMEL_CONFIG

    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0.01, le=1_000_000)
    product_category: str = Field(min_length=1, max_length=50)
    store_id: str = Field(min_length=1, max_length=50)
```

`Transaction` is the table model with `id`, `timestamp`, and `is_flagged`. `CustomerSegment` stores segment metadata. `SegmentPrediction` returns `customerId`, `predictedSegment`, `confidence`, and `topFeatures`.

## CamelCase JSON and validation

The Python models keep snake_case internally but serialise as camelCase on the wire, deliberately preserving the .NET contract:

```python
#: Serialize as camelCase but still accept snake_case when constructing in Python.
CAMEL_CONFIG = ConfigDict(alias_generator=to_camel, populate_by_name=True)
```

That is why API JSON uses `customerId`, `productCategory`, and `isFlagged`.

⚠️ SQLModel skips validation on `table=True` classes. The constrained fields therefore live on `TransactionBase`, inherited by both `Transaction` and `TransactionCreate`. FastAPI validates `TransactionCreate` before the router calls the service and returns HTTP 422 on invalid request bodies:

```python
class TransactionCreate(TransactionBase):
    """Request body for creating a transaction.

    FastAPI validates this automatically and returns HTTP 422 on failure, which
    is what ``ModelState.IsValid`` does in the .NET ``TransactionsController``.
    """
```

## Database and startup seeding

[`app/database.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/database.py) creates the SQLite engine and per-request session dependency:

```python
DATABASE_URL = "sqlite:///retail.db"

engine = create_engine(DATABASE_URL, echo=False)
```

[`app/main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py) seeds during the FastAPI lifespan handler:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed database on startup
    create_db_and_tables()
    with Session(engine) as session:
        await RetailAnalyticsService(session).seed_data()
```

The seed method returns immediately when transactions already exist, so normal demo restarts are idempotent.

## Seed data

The fixture contains 10 transactions across customers `C001` to `C005`:

| Customer | Seeded pattern |
| --- | --- |
| `C001` | Grocery and Electronics purchases totalling 335.49 |
| `C002` | Grocery and Health purchases totalling 47.50 |
| `C003` | Electronics and Fashion purchases totalling 1,700.00 |
| `C004` | Two low-value Grocery purchases totalling 21.49 |
| `C005` | Electronics and Fashion purchases totalling 995.00 |

It also creates four customer segments: High Value, Regular, At Risk, and New.

## REST endpoints

[`app/routers/transactions.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/transactions.py) exposes transaction read, create, and delete endpoints:

| Endpoint | Returns |
| --- | --- |
| `GET /api/transactions` | All `Transaction` records. |
| `GET /api/transactions/{id}` | One `Transaction`, or `404` if not found. |
| `POST /api/transactions` | Creates a transaction and returns `201 Created` with the saved record. |
| `DELETE /api/transactions/{id}` | `204 No Content` when deleted, or `404` when not found. |

[`app/routers/segments.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/segments.py) exposes `GET /api/segments`, `GET /api/segments/{segment_id}`, and `GET /api/segments/predict/{customer_id}`.

The chat endpoints are covered in [Streaming responses over SSE](./02-sse-streaming.md), because they belong to the Copilot streaming path rather than the retail data API.

## Segment prediction logic

[`RetailAnalyticsService.predict_segment`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py) loads all transactions for a customer and derives total spend, average spend, and purchase frequency. It then applies these rules in order:

1. No transactions: return `New` with confidence `0.5` and `no_history`.
2. Total spend above `1000`: return `High Value` with confidence `0.89`.
3. Frequency of three or more: return `Regular` with confidence `0.75`.
4. Average spend below `50`: return `At Risk` with confidence `0.62`.
5. Otherwise: return `Regular` with confidence `0.55`.

The returned `topFeatures` array explains the rule inputs, such as total spend, frequency, or average spend.

## Try it with curl

Real verified outputs:

```bash
$ curl http://localhost:5060/api/segments/predict/C003
{"customerId":"C003","predictedSegment":"High Value","confidence":0.89,"topFeatures":["high_total_spend","multi_category","total_1700"]}

$ curl http://localhost:5060/api/segments/predict/C999
{"customerId":"C999","predictedSegment":"New","confidence":0.5,"topFeatures":["no_history"]}

$ curl http://localhost:5060/api/transactions/1
{"productCategory":"Grocery","customerId":"C001","amount":245.5,"isFlagged":false,"storeId":"S001","id":1,"timestamp":"2026-07-14T03:58:08.543810"}
```

`GET /api/transactions` returns 10 rows. `GET /api/segments` returns 4 rows. `GET /api/transactions/999` returns HTTP 404.

## Tests

The pytest suite mirrors the .NET xUnit tests, plus four Python-only contract
tests guarding the browser/API request shape. Real verified test result:

```bash
$ uv run pytest
18 passed
```

## Four deliberate code smells

These are intentional demo material for code-review sessions. Do not present them as accidental bugs to fix during this demo; use them as examples of what a reviewer should notice and explain. They mirror the .NET versions so the same answer key applies.

### 1. N+1 query in `get_transactions_with_segments`

What it is: the method loads all transactions, then loops through each transaction and calls `predict_segment`, which runs another database query for that customer.

```python
for txn in transactions:
    # N+1: querying segments for every single transaction
    segment = await self.predict_segment(txn.customer_id)
```

Why it is a problem: query count grows with transaction count. A reviewer should recommend batching customer transaction data or calculating predictions from data already loaded for the request.

### 2. Missing null check in `get_transaction`

What it is: the service returns the result of `self._db.get(...)` even though the database can return no row.

```python
# Missing null check: will return None if not found
return self._db.get(Transaction, transaction_id)
```

Why it is a problem: callers cannot tell from the signature that `None` is possible. A reviewer should ask for `Transaction | None` or a result type, with explicit caller handling.

### 3. No input validation in `add_transaction`

What it is: the service accepts the supplied `Transaction`, stamps the timestamp, and saves it without checking amount, customer ID, category, or store values.

```python
# No validation: negative amounts and empty customer_id are allowed
transaction.timestamp = datetime.now(UTC)
self._db.add(transaction)
```

Why it is a problem: FastAPI validates `TransactionCreate`, but tests, other services, or future endpoints could call the service directly. A reviewer should recommend centralising domain invariants in the service or a policy.

### 4. Hardcoded threshold in `predict_segment`

What it is: the high-value rule uses the literal threshold `1000` in code.

```python
# BUG: Hardcoded magic number — should be configurable
if total_spend > 1000:
```

Why it is a problem: thresholds change by market, season, and retailer. A reviewer should move the threshold into configuration or a named policy object and cover the boundary behaviour in tests.

## Related

- [Embedding the Copilot SDK](./01-copilot-sdk-integration.md)
- [Streaming responses over SSE](./02-sse-streaming.md)
- [The web UI](./04-web-ui.md)
- Source: [`retail_analytics.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py), [`models.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/models.py), [`database.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/database.py), [`main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py), [`transactions.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/transactions.py), [`segments.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/segments.py), [`conftest.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/conftest.py), [`test_retail_analytics.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_retail_analytics.py), [`test_transaction_validation.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_transaction_validation.py)
