# Lab 07 — Wrap-up

**Goal:** consolidate what you built, tidy your machine, and choose a sensible
next step.

**Time:** ~10 minutes

## What you covered

| Lab | Capability |
|:----|:-----------|
| [01](../01-setup/) | Installed dependencies, ran the FastAPI app, and smoke-tested the SDK samples |
| [02](../02-first-chat/) | Traced a streaming chat turn and discovered models at runtime |
| [03](../03-tools/) | Replaced static context with Python `@define_tool` tools |
| [04](../04-events/) | Observed the session event lifecycle and completion signals |
| [05](../05-sessions/) | Persisted and resumed SDK sessions across process restarts |
| [06](../06-mcp/) | Connected MCP servers to extend the agent with external tools |

The optional `extra-*` labs now sit outside the main SDK path. Use them when
you want CLI custom agents, governance hooks, or FastAPI/SQLModel extension
practice, but they are not required for the SDK sequence.

## The ideas worth keeping

1. **Embedding beats chatting.** The SDK turns an agent into a component of
   your application, subject to your auth, your logging, and your deployment
   pipeline. In Python that starts with `CopilotClient()`, usually as
   `async with CopilotClient() as client:`; if you construct it manually, call
   `await client.start()` before creating sessions.

2. **Discover capabilities; don't hardcode them.** Models come from
   `await client.list_models()`, so readers do not all need access to the same
   preview model.

3. **Session creation is keyword-driven.** The call shape you saw repeatedly is
   `await client.create_session(model=..., streaming=..., system_message=..., tools=..., mcp_servers=..., on_permission_request=...)`.
   Those keyword-only arguments are the configuration surface for chat, tools,
   MCP, and permissions.

4. **Tools beat context-stuffing.** `@define_tool` lets the model fetch what it
   needs instead of pre-loading every turn with guesses that burn tokens whether
   they are useful or not. Python custom tools **require**
   `on_permission_request` or the call is denied; the .NET sample needs no such
   handler.

5. **Events are push-only.** `session.on(handler)` registers a callback and
   returns an unsubscribe callable. There is no async iterator, so the samples
   share `IdleWaiter` in
   [`sdk_labs/_common.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py) to wait for idle or error.

6. **Python has one event dataclass.** .NET pattern-matches on event subclasses;
   Python gives you one `SessionEvent` and you branch on `evt.type`, a
   `SessionEventType` enum. That is why the samples check
   `evt.type is SessionEventType.SESSION_IDLE`.

7. **Sending and completion are separate choices.** Use
   `await session.send(prompt)` when you want to watch events yourself. Use
   `await session.send_and_wait(prompt, timeout=...)` when you only need the SDK
   to wait for completion.

8. **Sessions make the agent portable.** `resume_session` plus
   `get_session_metadata` survives process restarts. The demo app's
   browser-localStorage history is convenient, but it cannot move between
   devices.

9. **MCP extends reach.** Python configures MCP servers as plain dictionaries —
   for example `mcp_servers={"microsoft.docs.mcp": {"type": "http", ...}}` —
   without baking every integration into your app. Unlike .NET, Python needs no
   `GHCP001` suppression for permission APIs.

## Clean up

Stop the service (`Ctrl+C` in the terminal), or if it was detached:

```bash
lsof -ti:5060        # prints a PID if still listening
kill <PID>
```

Remove local artefacts:

```bash
rm -f src/AgentOrchestrator-python/retail.db*   # SQLite DB + WAL files
rm -f logs/*                                    # if you ran the shared CLI extras
```

`retail.db` is created in the Python working directory on first run and is
gitignored. ⚠️ If a file is still open on macOS, the remove command may appear
to succeed while the service recreates it. Stop the service first, then remove
the artefact.

```bash
git status --short
```

Expected: no output, or only the lab files you intentionally edited. If you
want to discard local lab work and return to a clean checkout:

```bash
git status
git checkout -- .        # discards uncommitted changes — irreversible
```

## Check your understanding

1. Why does the Python track use `async with CopilotClient()`?
2. Why do the samples need `IdleWaiter` instead of `async for evt in session`?
3. What happens if a Python custom tool is registered without
   `on_permission_request`?
4. What event field do you inspect in Python, and what SDK calls prove a
   session can be resumed after restart?

<details>
<summary>Answers</summary>

1. It starts and stops the client reliably. If you do not use the context
   manager, call `await client.start()` and later `await client.stop()` yourself.
2. SDK events are push callbacks. `session.on(handler)` subscribes a handler, so
   a small future-based helper waits for `SESSION_IDLE` or raises on
   `SESSION_ERROR`.
3. The tool invocation is denied. Python requires a permission handler for
   custom tools; .NET does not require one for the equivalent sample.
4. Every event is a `SessionEvent`; branch on `evt.type`, a
   `SessionEventType` enum. `await client.resume_session(session_id, ...)`
   reopens the conversation and `await client.get_session_metadata(session_id)`
   retrieves the stored metadata.

</details>

## Where to go next

| Direction | Start here |
|:----------|:-----------|
| Re-run a focused SDK sample | [`sdk_labs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/__main__.py) |
| Understand the demo code in depth | [Demos](../../demos-python/) |
| Reference troubleshooting and architecture | [Breakouts](../../breakouts/) |
| Build your own agent app | [Copilot SDK repo](https://github.com/github/copilot-sdk) |
| Extend Copilot with external tools | [Model Context Protocol](https://modelcontextprotocol.io/) |

### Ideas to take further

- **Promote a sample into the app.** Move one `sdk_labs` command into a real API
  endpoint and add user-facing progress.
- **Persist conversations server-side.** Replace browser localStorage with
  SQLite-backed session metadata so history survives across devices.
- **Add a second MCP server.** Keep credentials out of source, document the
  required environment variables, and prove the tools appear at runtime.
- **Tighten observability.** Log the event types you ignore today so production
  debugging has enough context without storing full prompts.

## ✅ Final checkpoint

- [x] All seven SDK labs complete
- [x] Service stopped, local artefacts cleaned up
- [x] `git status --short` is clean, or only intentional lab edits remain
- [x] You can answer the four questions above

## Related

- [Labs index](../README.md)
- [Python app README](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md)
- [Troubleshooting](../../breakouts/troubleshooting.md)
- [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md)
