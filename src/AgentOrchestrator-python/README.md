# AgentHQ デモ — Python

AI Genius S5E2 小売分析スタックの Python 版です。
[`../AgentOrchestrator`](../AgentOrchestrator) の .NET プロジェクトと機能ごとに対応しており、
同じ API コントラクト、同じシードデータ、同じ意図的なコードスメル、
同じ実行可能な Copilot SDK ラボサンプルを備えています。

どちらか一方のトラックに取り組めばよく、両方を行う必要はありません。

| | .NET | Python |
|:--|:--|:--|
| Web フレームワーク | ASP.NET Core | FastAPI |
| ORM | EF Core | SQLModel |
| UI | Blazor WebAssembly | Static HTML + vanilla JS |
| テスト | xUnit (26) | pytest (30) |
| パッケージ管理 | `dotnet` | `uv` |
| ポート | 5050 API + 5051 UI | 5070（API と UI を同時に提供） |

ポートが重複しないため、両方のスタックを同時に実行できます。

## 前提条件

- **Python 3.11 以降**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python と依存関係をインストールします
- **[GitHub Copilot CLI](https://github.com/github/copilot-cli)** — サインイン済みである必要があります。
  SDK は Copilot CLI と通信します。Copilot CLI がなくてもデータエンドポイントとテストは動作しますが、
  チャットエンドポイントは失敗します。

## クイックスタート

```bash
cd src/AgentOrchestrator-python

uv sync                                        # install dependencies
uv run uvicorn app.main:app --port 5070        # start API + UI
```

<http://localhost:5070> を開きます。初回実行時にデータベースが作成され、シードデータが投入されます。

`--reload` を指定すると、編集中にホットリロードが有効になります。

```bash
uv run uvicorn app.main:app --port 5070 --reload
```

## テストと lint

```bash
uv run pytest          # 30 tests (14 domain + 12 MCP + 4 contract)
uv run ruff check .    # lint
```

## SDK ラボサンプル

各サブコマンドは、
[`docs/labs-python/`](../../docs/labs-python/README.md) の対応するラボで使用します。

```bash
uv run python -m sdk_labs tools       # Lab 03 — define a tool
uv run python -m sdk_labs events      # Lab 04 — session event lifecycle
uv run python -m sdk_labs sessions    # Lab 05 — persist and resume
uv run python -m sdk_labs mcp         # Lab 06 — attach an MCP server
```

モデルを選択するには `--model <id>` を追加します。たとえば、
`uv run python -m sdk_labs tools --model gpt-5` と指定します。省略した場合、サンプルは
アカウントで利用可能なモデルを確認し、`claude-haiku-4.5` を優先します。

`permissions` サブコマンドもあります。これは**ラボではなくリファレンスコード**です。
カスタムツールではハンドラーが呼び出されますが、ホストの Copilot CLI がすでにシェル実行を承認するため、
シェルコマンドでは呼び出しを確認できませんでした。注意事項の詳細は
[ラボ 03](../../docs/labs-python/03-tools/README.md)を参照してください。

`SDKLABS_TRACE_EVENTS=1` を設定すると、MCP サンプルが受信するすべてのイベントが出力されます。
サーバーに接続できない場合の最も簡単な診断方法です。

## API エンドポイント

.NET API と同じパスを使用するため、ラボ内のすべての `curl` はどちらのスタックでも動作します。

| メソッド | パス | 用途 |
|:--|:--|:--|
| `POST` | `/api/chat` | チャット（バッファリングされたレスポンス） |
| `POST` | `/api/chat/stream` | チャット（Server-Sent Events によるストリーミング） |
| `GET` | `/api/chat/models` | このアカウントで利用可能なモデル |
| `GET` | `/api/chat/health` | 正常性プローブ |
| `GET` | `/api/transactions` | すべてのトランザクション |
| `GET` | `/api/transactions/{id}` | 1 件のトランザクション |
| `POST` | `/api/transactions` | トランザクションの作成 |
| `DELETE` | `/api/transactions/{id}` | トランザクションの削除 |
| `GET` | `/api/segments` | すべての顧客セグメント |
| `GET` | `/api/segments/{id}` | 1 件のセグメント |
| `GET` | `/api/segments/predict/{customerId}` | 顧客セグメントの予測 |

JSON は .NET のコントラクトに合わせて camelCase（`customer_id` ではなく `customerId`）を使用します。

```bash
curl http://localhost:5070/api/transactions
curl http://localhost:5070/api/segments/predict/C003
```

## ディレクトリ構成

```
src/AgentOrchestrator-python/
├── app/
│   ├── main.py                     # FastAPI app, startup seeding, static mount
│   ├── database.py                 # SQLModel engine and session dependency
│   ├── models.py                   # Transaction, CustomerSegment, SegmentPrediction
│   ├── routers/                    # chat, transactions, segments
│   ├── services/
│   │   ├── copilot_chat.py         # Copilot SDK integration and SSE bridge
│   │   └── retail_analytics.py     # Business logic (contains the code smells)
│   └── static/                     # Chat UI
├── sdk_labs/                       # Runnable samples for labs 03-06
└── tests/                          # pytest suite
```

## セキュリティに関する注意

`app/services/retail_analytics.py` には、コードレビューとエージェントのラボで使用する
**4 つの意図的な問題**があります。デモの一部であるため、安易に修正しないでください。

1. `get_transactions_with_segments` の **N+1 クエリ**
2. `get_transaction` の **`None` チェック不足**
3. `add_transaction` の **入力検証不足**
4. `predict_segment` の **ハードコードされたしきい値**

これらは .NET 版と正確に対応しているため、どちらのトラックにも同じ解答例を使用できます。

## Python 固有の注意事項

Python SDK と .NET の相違点として理解しておくべき事項があります。

- **イベントは階層ではなく単一の型です。** .NET ではイベントのサブクラスをパターンマッチしますが、
  Python では 1 つの `SessionEvent` を受け取り、`SessionEventType` 列挙型の
  `evt.type` で分岐します。
- **試験的 API のオプトインは不要です。** .NET サンプルでは権限判定を使用するために `GHCP001`
  ビルドエラーを抑制する必要があります。Python では同じ判定が `copilot.rpc` から公開され、
  同等の手順は不要です。
- **カスタムツールには権限ハンドラーが必要です。** `create_session(...)` に
  `on_permission_request` を渡さないと、カスタムツールの呼び出しは拒否されます。
  .NET サンプルでは、このハンドラーは不要です。

SDK イベントは非同期イテレーターではなくプッシュコールバックとして届くため、
`copilot_chat.py` は `session.on(...)` で受け取ったイベントを `asyncio.Queue` に橋渡しし、
非同期ジェネレーターがキューから順次取り出します。これは、C# サービスが `Channel` に書き込む方法と同じ考え方です。
