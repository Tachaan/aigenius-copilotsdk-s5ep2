# /docs

Documentation and step-by-step content for the session, organised into three
sections.

## 📚 Sections

| Section | What it is | Start here |
|:--------|:-----------|:-----------|
| [**Labs**](labs/) | Numbered hands-on exercises, ~2 hours end to end | [Lab 01 — Setup](labs/01-setup/) |
| [**Demos**](demos/) | Walkthroughs explaining the code in [`/src`](../src/AgentOrchestrator/) | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| [**Breakouts**](breakouts/) | Diagrams, configuration reference, troubleshooting | [Architecture](breakouts/architecture.md) |

### Labs

| # | Lab | Time |
|:--|:----|:-----|
| 01 | [Setup](labs/01-setup/) — build, run, verify | ~15 min |
| 02 | [First chat](labs/02-first-chat/) — SSE streaming and runtime models | ~20 min |
| 03 | [Custom agents](labs/03-custom-agents/) — agent-assisted code review | ~20 min |
| 04 | [Governance hooks](labs/04-governance-hooks/) — make the security gate fire | ~20 min |
| 05 | [Extend the API](labs/05-extend-api/) — new endpoint with tests | ~30 min |
| 06 | [Wrap-up](labs/06-wrap-up/) — consolidate and clean up | ~10 min |

### Demos

| # | Walkthrough |
|:--|:------------|
| 01 | [Copilot SDK integration](demos/01-copilot-sdk-integration.md) |
| 02 | [SSE streaming](demos/02-sse-streaming.md) |
| 03 | [Retail analytics](demos/03-retail-analytics.md) |
| 04 | [Blazor UI](demos/04-blazor-ui.md) |
| — | [Demo script](demos/demo-script.md) — presenter talk track |

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

- **Labs** — one folder per exercise, numbered: `07-your-topic/README.md`
- **Demos** — one file per area of the codebase, numbered
- **Breakouts** — one file per reference topic, named not numbered
- Keep images in `screenshots/` or an `assets/` subfolder
- Update the tables above and the relevant section `README.md`

## Content rules

- **No large binaries** — no PowerPoint decks, videos, or recordings. Link to
  them instead.
- **Nothing confidential** — no customer names, competitive analysis, account
  plans, or internal-only material. See [`AGENTS.md`](../AGENTS.md).
- **Don't "fix" the intentional code smells** — four flawed patterns exist
  deliberately for review demonstrations.

## Licensing

Documentation in this folder is licensed under
[CC BY 4.0](../LICENSE-DOCS). Source code in `/src` is licensed separately
under the [MIT License](../LICENSE).
