# Python demos

Walkthroughs of the Python code in
[`src/AgentOrchestrator-python/README.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md).
Read these to understand *how* the FastAPI version of the Agent HQ demo works —
the [Python labs](../labs-python/) are the hands-on counterpart.

## Walkthroughs

| # | Doc | Covers |
|:--|:----|:-------|
| 01 | [Copilot SDK integration](01-copilot-sdk-integration.md) | `CopilotChatService` — client lifecycle, session events, callback-to-queue streaming, runtime model discovery |
| 02 | [SSE streaming](02-sse-streaming.md) | `app.routers.chat` → browser: wire format, `StreamingResponse`, error contract |
| 03 | [Retail analytics](03-retail-analytics.md) | SQLModel models, SQLite, seeding, prediction, validation, and the intentional code smells |
| 04 | [Web UI](04-web-ui.md) | Static HTML, vanilla JavaScript, model picker, localStorage, streaming render |

## Suggested order

If you're new to the Python stack, read them in numbered order — each assumes the
previous. If you already know the .NET track, start with the SDK integration page
and skim for Python-vs-.NET differences.

## ⚠️ On the intentional code smells

[Walkthrough 03](03-retail-analytics.md) documents four flawed patterns that
exist **on purpose** for code-review demonstrations. They are not bugs to fix.
The Python service mirrors the .NET service so the same answer key applies.

## Related

- [.NET demos](../demos/) — the original Blazor + ASP.NET Core walkthroughs
- [Python labs](../labs-python/) — hands-on exercises covering this same ground
- [Breakouts](../breakouts/) — architecture diagrams and reference material
- [Architecture](../breakouts/architecture.md) — the system at a glance
