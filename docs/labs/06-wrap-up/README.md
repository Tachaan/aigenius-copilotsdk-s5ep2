# Lab 06 — Wrap-up

**Goal:** consolidate what you built, tidy your machine, and choose a sensible
next step.

**Time:** ~10 minutes

## What you covered

| Lab | Capability |
|:----|:-----------|
| [01](../01-setup/) | Built and ran a .NET 10 app with the Copilot SDK embedded |
| [02](../02-first-chat/) | Traced a prompt through SSE streaming; discovered models at runtime |
| [03](../03-custom-agents/) | Used custom agents to review code against checked-in standards |
| [04](../04-governance-hooks/) | Made a `preToolUse` gate genuinely block secrets, with an audit trail |
| [05](../05-extend-api/) | Extended the API with Copilot while keeping the suite green |

## The five ideas worth keeping

1. **Embedding beats chatting.** The SDK turns an agent into a component of
   your application, subject to your auth, your logging, and your deployment
   pipeline.

2. **Discover capabilities; don't hardcode them.** This demo once shipped six
   hardcoded model ids and quietly degraded to one working option. Asking the
   CLI at runtime can't drift.

3. **Streaming is a UX contract.** Missing a single `FlushAsync` turns
   token-by-token output into a long pause and one big blob. And once headers
   are sent, errors must travel *inside* the stream.

4. **Standards belong in version control.** `copilot-instructions.md`,
   `.agent.md` files, and skills mean every reviewer — human or agent — applies
   the same rules.

5. **Verify your controls actually fire.** The `preToolUse` gate pointed at a
   script that didn't exist. Nothing errored; it just silently never ran, while
   the repo looked governed. Untested controls are theatre.

## Clean up

Stop the services (`Ctrl+C` in each terminal), or if they were detached:

```bash
lsof -ti:5050        # prints a PID if still listening
kill <PID>
lsof -ti:5051
kill <PID>
```

Remove local artefacts:

```bash
rm -f src/AgentOrchestrator/AgentHQDemo.Api/retail.db*   # SQLite DB + WAL files
rm -f .env                                               # if you created one in Lab 04
rm -rf logs/*.log logs/*.jsonl                           # audit + denial logs
```

⚠️ `.env` is gitignored, but confirm it never got committed:

```bash
git status --short
git log --oneline --all -- .env      # should print nothing
```

Reset your working tree if you want to discard the Lab 05 work:

```bash
git status
git checkout -- .        # discards uncommitted changes — irreversible
```

## Check your understanding

1. Why does `CopilotChatService` bridge SDK events through a `Channel<string>`
   instead of yielding directly from the event handler?
2. Why are streaming errors sent as `data: {"error":...}` rather than an HTTP
   500?
3. What compile error appears if you write `session.On(evt => ...)` without the
   type argument, and why did it work in older samples?
4. Which of the four hook events can actually block a tool call?
5. Why does the segment summary weight retention by customer count instead of
   taking a plain mean?

<details>
<summary>Answers</summary>

1. C# forbids `yield return` inside a `try`/`catch`. The session work needs
   exception handling, so it runs in a background `Task` and pushes chunks onto
   a channel the enumerator drains.
2. The status line and headers are flushed with the first chunk, so no status
   code remains to change. The error has to ride in the stream body.
3. `CS0411` — the type argument can't be inferred. SDK v1.x requires
   `On<SessionEvent>(...)`; v0.x samples predate that change, which also moved
   the namespace from `GitHub.Copilot.SDK` to `GitHub.Copilot`.
4. Only `preToolUse`. `sessionStart`, `postToolUse`, and `sessionEnd` observe
   but cannot deny.
5. Segments differ enormously in size — 150 customers versus 3,200. A plain
   mean gives 0.70 and over-weights tiny segments; weighting gives ≈0.71 and
   reflects the actual customer base.

</details>

## Where to go next

| Direction | Start here |
|:----------|:-----------|
| Understand the code in depth | [Demos](../../demos/) |
| Reference the architecture | [Breakouts](../../breakouts/) |
| Present this yourself | [Demo script](../../demos/demo-script.md) |
| Build your own agent app | [Copilot SDK repo](https://github.com/github/copilot-sdk) |
| Extend Copilot's behaviour | [Awesome Copilot](https://github.com/github/awesome-copilot) |

### Ideas to take further

- **Add tool calling.** Let the model query the transaction database directly
  instead of receiving context in a system message.
- **Persist conversations.** Move chat history from browser localStorage into
  SQLite so it survives across devices.
- **Harden the gate.** Add rules for force-pushes and dependency changes, then
  add a CI check asserting every script referenced in
  `retail-governance.json` exists — the failure mode from Lab 04.
- **Fix the smells properly.** In a throwaway branch, repair all four issues
  and have `dotnet-reviewer` verify. Don't merge it.

## ✅ Final checkpoint

- [x] All six labs complete
- [x] Services stopped, local artefacts cleaned up
- [x] No secrets committed
- [x] You can answer the five questions above

## Related

- [Labs index](../README.md)
- [Root README](../../../README.md)
- [`AGENTS.md`](../../../AGENTS.md)
