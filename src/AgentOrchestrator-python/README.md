# AgentHQ Demo — Python

Python version of the AI Genius S5E2 retail analytics stack. It mirrors the
.NET project in [`../AgentOrchestrator`](../AgentOrchestrator) feature for
feature: same API contract, same seed data, same deliberate code smells, and
the same runnable Copilot SDK samples behind the labs.

Work either track — you do not need both.

| | .NET | Python |
|:--|:--|:--|
| Web framework | ASP.NET Core | FastAPI |
| ORM | EF Core | SQLModel |
| UI | Blazor WebAssembly | Static HTML + vanilla JS |
| Tests | xUnit (14) | pytest (14) |
| Packaging | `dotnet` | `uv` |
| Ports | 5050 API + 5051 UI | 5060 (API and UI together) |

Both stacks can run at the same time — the ports do not overlap.

## Prerequisites

- **Python 3.11 or later**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — installs
  Python and dependencies
- **[GitHub Copilot CLI](https://github.com/github/copilot-cli)**, signed in.
  The SDK talks to this; without it the chat endpoints fail but the data
  endpoints and tests still work.

## Quick start

```bash
cd src/AgentOrchestrator-python

uv sync                                        # install dependencies
uv run uvicorn app.main:app --port 5060        # start API + UI
```

Open <http://localhost:5060>. The database is created and seeded on first run.

`--reload` gives you hot reload while editing:

```bash
uv run uvicorn app.main:app --port 5060 --reload
```

## Tests and linting

```bash
uv run pytest          # 18 tests (14 domain + 4 contract)
uv run ruff check .    # lint
```

## SDK lab samples

Each subcommand backs one lab in
[`docs/labs-python/`](../../docs/labs-python/README.md):

```bash
uv run python -m sdk_labs tools       # Lab 03 — define a tool
uv run python -m sdk_labs events      # Lab 04 — session event lifecycle
uv run python -m sdk_labs sessions    # Lab 05 — persist and resume
uv run python -m sdk_labs mcp         # Lab 06 — attach an MCP server
```

Add `--model <id>` to pick a model, for example
`uv run python -m sdk_labs tools --model gpt-5`. Without it, the sample asks
your account which models are available and prefers `claude-haiku-4.5`.

There is also a `permissions` subcommand. It is **reference code, not a lab** —
the handler fires for custom tools but was not observed firing for shell
commands, because the host Copilot CLI already grants shell approval. See
[Lab 03](../../docs/labs-python/03-tools/README.md) for the full caveat.

`SDKLABS_TRACE_EVENTS=1` prints every event the MCP sample sees, which is the
quickest way to diagnose a server that will not connect.

## API endpoints

Identical paths to the .NET API, so every `curl` in the labs works against
either stack.

| Method | Path | Purpose |
|:--|:--|:--|
| `POST` | `/api/chat` | Chat, buffered response |
| `POST` | `/api/chat/stream` | Chat, streamed as Server-Sent Events |
| `GET` | `/api/chat/models` | Models this account can use |
| `GET` | `/api/chat/health` | Health probe |
| `GET` | `/api/transactions` | All transactions |
| `GET` | `/api/transactions/{id}` | One transaction |
| `POST` | `/api/transactions` | Create a transaction |
| `DELETE` | `/api/transactions/{id}` | Delete a transaction |
| `GET` | `/api/segments` | All customer segments |
| `GET` | `/api/segments/{id}` | One segment |
| `GET` | `/api/segments/predict/{customerId}` | Predict a customer's segment |

JSON is camelCase (`customerId`, not `customer_id`) to match the .NET contract.

```bash
curl http://localhost:5060/api/transactions
curl http://localhost:5060/api/segments/predict/C003
```

## Layout

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

## Security notes

`app/services/retail_analytics.py` contains **four deliberate issues** used by
the code review and agent labs. Do not fix them casually — they are the demo:

1. **N+1 query** in `get_transactions_with_segments`
2. **Missing null check** in `get_transaction`
3. **No input validation** in `add_transaction`
4. **Hardcoded threshold** in `predict_segment`

These mirror the .NET versions exactly, so the same answer key applies to both
tracks.

## Python-specific notes

Two places where the Python SDK differs from .NET in ways worth understanding:

- **Events are a single type, not a hierarchy.** .NET pattern-matches on event
  subclasses; Python gives you one `SessionEvent` and you branch on
  `evt.type`, a `SessionEventType` enum.
- **No experimental-API opt-in.** The .NET samples must suppress the `GHCP001`
  build error to use permission decisions. Python exposes the same decisions
  from `copilot.rpc` with no equivalent step.
- **Custom tools need a permission handler.** `create_session(...)` must be
  given `on_permission_request` or a custom tool call is denied. The .NET
  sample needs no such handler.

Because SDK events arrive as push callbacks with no async iterator,
`copilot_chat.py` bridges `session.on(...)` into an `asyncio.Queue` and drains
it as an async generator — the same idea as the C# service writing into a
`Channel`.
