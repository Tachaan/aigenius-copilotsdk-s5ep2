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

Documentation is grouped **by track first** — .NET and Python are peers, and the
material that belongs to neither sits in Breakouts.

| Section | What it is | Start here |
|:--------|:-----------|:-----------|
| [**.NET — Labs**](labs/) | Hands-on Copilot SDK exercises, ~2 hours end to end | [Lab 01 — Setup](labs/01-setup/) |
| [**.NET — Demos**](demos/) | Walkthroughs explaining the code in [`src/AgentOrchestrator`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator) | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| [**Python — Labs**](labs-python/) | The same exercises against the Python SDK | [Lab 01 — Setup](labs-python/01-setup/) |
| [**Python — Demos**](demos-python/) | Walkthroughs explaining the code in [`src/AgentOrchestrator-python`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator-python) | [Copilot SDK integration](demos-python/01-copilot-sdk-integration.md) |
| [**Breakouts**](breakouts/) | Reference and the shared Copilot CLI labs | [Architecture](breakouts/architecture.md) |

### .NET — the SDK path

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

### .NET — demos

| # | Walkthrough |
|:--|:------------|
| 01 | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| 02 | [SSE streaming](demos/02-sse-streaming.md) |
| 03 | [Retail analytics](demos/03-retail-analytics.md) |
| 04 | [Blazor UI](demos/04-blazor-ui.md) |

### Python — the SDK path

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

### Python — demos

| # | Walkthrough |
|:--|:------------|
| 01 | [Copilot SDK integration](demos-python/01-copilot-sdk-integration.md) |
| 02 | [SSE streaming](demos-python/02-sse-streaming.md) |
| 03 | [Retail analytics](demos-python/03-retail-analytics.md) |
| 04 | [Web UI](demos-python/04-web-ui.md) |

### Track-specific extras

Optional. [Extend the API](labs/extra-extend-api/) exists once per track and
covers general app development rather than the SDK:
[.NET](labs/extra-extend-api/) · [Python](labs-python/extra-extend-api/)

### Breakouts

Reference, plus everything that belongs to neither track.

**Reference** —
[Architecture](breakouts/architecture.md) ·
[Custom agents](breakouts/custom-agents.md) ·
[Hooks and governance](breakouts/hooks-and-governance.md) ·
[Skills](breakouts/skills.md) ·
[Troubleshooting](breakouts/troubleshooting.md)

**Hands-on extras** — Copilot **CLI** labs, language-agnostic, so they live here
instead of being duplicated per track:
[Custom agents](labs/extra-custom-agents/) ·
[Governance hooks](labs/extra-governance-hooks/)

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

The site nav is grouped **by track** (`.NET`, `Python`), not by folder, so a new
page goes under the track it belongs to. Anything language-agnostic — CLI
material, reference, presenter notes — goes under `Breakouts`, even if the file
itself lives in `labs/` or `demos/`. Folder names are kept as-is because
cross-links, `scripts/build_index.py`, and the link checker depend on them.

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
