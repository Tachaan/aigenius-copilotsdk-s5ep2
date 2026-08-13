# /docs

Documentation and step-by-step content for the session.

## 🐍 or #️⃣ — pick a track

The same application is implemented twice. Both tracks teach identical Copilot
SDK concepts and expose an identical HTTP contract, so **work one, not both**.

| Track | Stack | Labs | Demos |
|:------|:------|:-----|:------|
| **.NET** | .NET 10, ASP.NET Core, Blazor WebAssembly | [labs/](labs/) | [demos/](demos/) |
| **Python** | Python 3.11+, FastAPI, static HTML + JS | [labs-python/](labs-python/) | [demos-python/](demos-python/) |

The ports differ (5050/5051 vs 5070), so both stacks can run side by side if you
want to compare them.

## 📚 Sections

| Section | What it is | Start here |
|:--------|:-----------|:-----------|
| [**Labs — .NET**](labs/) | Hands-on Copilot SDK exercises, ~2 hours end to end | [Lab 01 — Setup](labs/01-setup/) |
| [**Labs — Python**](labs-python/) | The same exercises against the Python SDK | [Lab 01 — Setup](labs-python/01-setup/) |
| [**Demos — .NET**](demos/) | Walkthroughs explaining the code in [`src/AgentOrchestrator`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator) | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| [**Demos — Python**](demos-python/) | Walkthroughs explaining the code in [`src/AgentOrchestrator-python`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator-python) | [Copilot SDK integration](demos-python/01-copilot-sdk-integration.md) |
| [**Breakouts**](breakouts/) | Diagrams, configuration reference, troubleshooting | [Architecture](breakouts/architecture.md) |

### Labs — the SDK path (.NET)

| # | Lab | Time |
|:--|:----|:-----|
| 01 | [Setup](labs/01-setup/) — build, run, verify | ~15 min |
| 02 | [First chat](labs/02-first-chat/) — SSE streaming and runtime models | ~20 min |
| 03 | [Tools](labs/03-tools/) — `CopilotTool.DefineTool` | ~20 min |
| 04 | [Events](labs/04-events/) — the session event lifecycle | ~20 min |
| 05 | [Sessions](labs/05-sessions/) — persistence and resume | ~20 min |
| 06 | [MCP](labs/06-mcp/) — attach an MCP server | ~20 min |
| 07 | [Wrap-up](labs/07-wrap-up/) — consolidate and clean up | ~10 min |

Backed by a runnable samples project at
[`src/AgentOrchestrator/samples/SdkLabs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/samples/SdkLabs).

### Labs — the SDK path (Python)

| # | Lab | Time |
|:--|:----|:-----|
| 01 | [Setup](labs-python/01-setup/) — install, run, verify | ~15 min |
| 02 | [First chat](labs-python/02-first-chat/) — SSE streaming and runtime models | ~20 min |
| 03 | [Tools](labs-python/03-tools/) — `@define_tool` | ~20 min |
| 04 | [Events](labs-python/04-events/) — the session event lifecycle | ~20 min |
| 05 | [Sessions](labs-python/05-sessions/) — persistence and resume | ~20 min |
| 06 | [MCP](labs-python/06-mcp/) — attach an MCP server | ~20 min |
| 07 | [Wrap-up](labs-python/07-wrap-up/) — consolidate and clean up | ~10 min |

Backed by a runnable samples package at
[`src/AgentOrchestrator-python/sdk_labs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator-python/sdk_labs).

### Labs — extras (not the SDK)

Optional. These cover Copilot **CLI** and general app development.

[Custom agents](labs/extra-custom-agents/) ·
[Governance hooks](labs/extra-governance-hooks/) ·
[Extend the API — .NET](labs/extra-extend-api/) ·
[Extend the API — Python](labs-python/extra-extend-api/)

Custom agents and governance hooks are Copilot CLI features and therefore
language-agnostic — the Python track links to them rather than duplicating them.

### Demos — .NET

| # | Walkthrough |
|:--|:------------|
| 01 | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| 02 | [SSE streaming](demos/02-sse-streaming.md) |
| 03 | [Retail analytics](demos/03-retail-analytics.md) |
| 04 | [Blazor UI](demos/04-blazor-ui.md) |
| — | [Demo script](demos/demo-script.md) — presenter talk track |

### Demos — Python

| # | Walkthrough |
|:--|:------------|
| 01 | [Copilot SDK integration](demos-python/01-copilot-sdk-integration.md) |
| 02 | [SSE streaming](demos-python/02-sse-streaming.md) |
| 03 | [Retail analytics](demos-python/03-retail-analytics.md) |
| 04 | [Web UI](demos-python/04-web-ui.md) |

### Breakouts

[Architecture](breakouts/architecture.md) ·
[Custom agents](breakouts/custom-agents.md) ·
[Hooks and governance](breakouts/hooks-and-governance.md) ·
[Skills](breakouts/skills.md) ·
[Troubleshooting](breakouts/troubleshooting.md)

## 🖼️ Assets

| Path | Purpose |
|:-----|:--------|
| `Slide1.png` – `Slide3.png` | Session slides — the "Three Mondays" narrative |
| `screenshots/` | UI screenshots referenced from the README |

## Adding content

- **Labs** — one folder per exercise, numbered: `07-your-topic/README.md`.
  `labs/` is the .NET track, `labs-python/` is the Python track.
- **Demos** — one file per area of the codebase, numbered.
  `demos/` is .NET, `demos-python/` is Python.
- **Breakouts** — one file per reference topic, named not numbered
- Keep images in `screenshots/` or an `assets/` subfolder
- Update the tables above, the relevant section `README.md`, and the `nav:`
  block in [`mkdocs.yml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/mkdocs.yml)

## Content rules

- **No large binaries** — no PowerPoint decks, videos, or recordings. Link to
  them instead.
- **Nothing confidential** — no customer names, competitive analysis, account
  plans, or internal-only material. See [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md).
- **Don't "fix" the intentional code smells** — four flawed patterns exist
  deliberately for review demonstrations, mirrored in both tracks.

## Licensing

Documentation in this folder is licensed under
[CC BY 4.0](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/LICENSE-DOCS). Source code in `/src` is licensed separately
under the [MIT License](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/LICENSE).
