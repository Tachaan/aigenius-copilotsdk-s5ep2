# Labs

Hands-on exercises for the **AI Genius S5E2 — Agent HQ Demo**. Work through
them in order; each builds on the previous one.

## Prerequisites

| Requirement | Notes |
|:------------|:------|
| [.NET 10 SDK](https://dotnet.microsoft.com/download) | `dotnet --version` should report `10.x` |
| [GitHub Copilot CLI](https://docs.github.com/copilot) | `npm install -g @github/copilot`, signed in with Copilot access |
| `git`, `curl`, `jq` | `jq` is used by the governance hooks |
| A terminal + editor | VS Code recommended — the repo ships `.vscode/mcp.json` |

Verify before you start:

```bash
dotnet --version     # 10.x
copilot --version    # 1.x
jq --version         # any recent version
```

## The path

| # | Lab | What you'll do | Time |
|:--|:----|:---------------|:-----|
| 01 | [Setup](01-setup/) | Build, run both services, verify the API and a live SSE stream | ~15 min |
| 02 | [First chat](02-first-chat/) | Trace a prompt through the Copilot SDK and switch models | ~20 min |
| 03 | [Custom agents](03-custom-agents/) | Use the custom agents to review the deliberate code smells | ~20 min |
| 04 | [Governance hooks](04-governance-hooks/) | Make the security gate block a secret and audit the session | ~20 min |
| 05 | [Extend the API](05-extend-api/) | Add an endpoint and tests without breaking the suite | ~30 min |
| 06 | [Wrap-up](06-wrap-up/) | Review, clean up, and pick a next step | ~10 min |

Total: roughly two hours at a comfortable pace.

## Conventions used in these labs

- Commands are written to be **copy-pasteable** from the repository root
- Expected output is shown so you can confirm each step worked
- ⚠️ marks something that will bite you if skipped
- 💡 marks optional extra credit

## ⚠️ Before you "fix" anything

This repository **intentionally** contains four flawed code patterns used for
code-review demonstrations:

- N+1 query in `GetTransactionsWithSegmentsAsync`
- Missing null check in `GetTransactionAsync`
- No input validation in `AddTransactionAsync`
- Hardcoded threshold in `PredictSegmentAsync`

Lab 03 asks you to *find* them. Do not repair them — later labs and the demo
script rely on them still being there. See [`AGENTS.md`](../../AGENTS.md).

## Related

- [Demos](../demos/) — walkthroughs of the code these labs touch
- [Breakouts](../breakouts/) — architecture, agents, hooks, and troubleshooting
- [Troubleshooting](../breakouts/troubleshooting.md) — start here when a step fails
