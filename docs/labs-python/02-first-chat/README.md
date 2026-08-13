# Lab 02 — Your first streaming chat

**Goal:** follow a single prompt all the way through the Python stack — HTTP
client → FastAPI → Copilot SDK → model → back — and understand why model
discovery is runtime data rather than a hardcoded list.

**Time:** ~20 minutes

**Prerequisites:** [Lab 01](../01-setup/) complete, with the FastAPI server
running on port 5070.

## Step 1 — Start or confirm the server

From the repository root:

```bash
cd src/AgentOrchestrator-python
uv run uvicorn app.main:app --port 5070
```

Open <http://localhost:5070> if you want to watch the UI later. The same
process serves both the API and static UI.

Confirm the API is healthy:

```bash
curl http://localhost:5070/api/chat/health
```

Expected:

```json
{"status":"healthy","service":"CopilotChat","availableModels":["claude-haiku-4.5","gpt-4.1","gpt-5","claude-sonnet-4.5","claude-opus-4.5","gemini-2.5-pro"]}
```

That fallback list is deliberately small. The real model picker asks your
signed-in Copilot account what it can use.

## Step 2 — Watch the wire format

Send a prompt and observe the raw Server-Sent Events:

```bash
curl -sN -X POST http://localhost:5070/api/chat/stream \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"Reply with exactly: streaming works","model":"claude-haiku-4.5"}'
```

Captured output:

```text
data: {"content": "streaming works"}

data: [DONE]
```

Three things to notice: each frame is `data: ` plus JSON, followed by a
**blank line**; a longer answer arrives as several frames because chunks can
split anywhere; and the stream ends with `data: [DONE]`.

⚠️ The request model is `prompt`, `model`, and optional `systemMessage`. An
unrecognised key such as `message` is silently ignored — you will get a generic
greeting back rather than a validation error.

## Step 3 — Find the server side

Open
[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py)
and locate `stream_chat`.

`stream_chat` returns a `StreamingResponse` with media type
`text/event-stream`. Inside `event_stream`, each SDK chunk is serialised as an
SSE frame:

```python
yield f"data: {json.dumps({'content': chunk})}\n\n"
```

The route then writes the `data: [DONE]` terminator.

⚠️ The blank line is not decoration. It is the event delimiter. Remove it and
many SSE clients will keep buffering because they never see a complete event.

Now look at the `except` block. Errors are written **into the stream** as
`data: {"error": "..."}`. Once an SSE response has started, the status line and
headers are already gone, so an HTTP 500 is no longer useful to the client.

## Step 4 — Find the SDK integration

Open
[`app/services/copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py).

`CopilotChatService.chat_stream` creates a session with streaming enabled:

```python
session = await self._client.create_session(
    model=model,
    streaming=True,
    system_message=(
        {"mode": "append", "content": system_message} if system_message else None
    ),
)
```

Then it subscribes to events:

```python
def on_event(evt: SessionEvent) -> None:
    # Unlike .NET, every event arrives as one SessionEvent
    # carrying a `type` enum and a `data` payload, so this
    # dispatches on `evt.type` rather than on subclasses.
    if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
        queue.put_nowait(evt.data.delta_content or "")
    elif evt.type is SessionEventType.ASSISTANT_MESSAGE:
        logger.info(
            "Assistant response complete: %d chars",
            len(evt.data.content or ""),
        )
    elif evt.type is SessionEventType.SESSION_IDLE:
        if not done.done():
            done.set_result(None)
    elif evt.type is SessionEventType.SESSION_ERROR:
        logger.error("Session error: %s", evt.data.message)
        if not done.done():
            done.set_exception(RuntimeError(evt.data.message))
```

The queue is the bridge between the SDK's callback style and FastAPI's async
response generator. The callback pushes chunks into `asyncio.Queue`; the route
awaits the queue and yields SSE frames.

## Step 5 — Understand Python events

This is the first important Python-vs-.NET difference.

.NET samples pattern-match event subclasses such as `AssistantMessageDeltaEvent`
and `SessionIdleEvent`. Python gives you one `SessionEvent` dataclass with
fields such as:

- `type`
- `data`
- `id`
- `timestamp`

The `type` field is a `SessionEventType` enum, so Python code branches like this:

```python
if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
    ...
elif evt.type is SessionEventType.SESSION_ERROR:
    ...
```

Events are also **push-only callbacks**. `session.on(handler)` returns an
unsubscribe callable; there is no async iterator to loop over directly.

The helper in
[`sdk_labs/_common.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py)
uses this pattern to wait until `SESSION_IDLE` or raise on `SESSION_ERROR`.

## Step 6 — Ask the API which models you have

```bash
curl -s http://localhost:5070/api/chat/models | jq -r '.[].id'
```

`/api/chat/models` returns a JSON **list** of objects shaped like:

```json
{"id":"...","name":"...","description":"..."}
```

The route first asks `CopilotChatService.list_models()`, which calls
`await client.list_models()`. That returns `ModelInfo` objects with `.id` and
`.name` fields.

⚠️ `list_models()` has a known upstream bug: it can raise
`ValueError: Missing required field 'multiplier' in ModelBilling`
(github/copilot-sdk#1302). The router catches broadly and falls back to the
static catalogue so the UI still has choices.

## Step 7 — Switch models and compare

Pick a model id from your live list:

```bash
MODEL=$(curl -s http://localhost:5070/api/chat/models | jq -r '.[0].id')
echo "Using $MODEL"

curl -sN -X POST http://localhost:5070/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d "{\"prompt\":\"In one sentence, what is customer churn?\",\"model\":\"$MODEL\"}"
```

Repeat with a different id and compare latency, style, and tone.

The sample model picker in
[`sdk_labs/model_picker.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/model_picker.py)
uses the same idea: prefer `claude-haiku-4.5`, but fall back to a concrete model
your account can actually use. You can override samples with `--model <id>`.

## Step 8 — Shape the response with a system message

The API accepts optional `systemMessage`. The service sends it in **append** mode
so it supplements the session's built-in instructions rather than replacing
them.

```bash
curl -sN -X POST http://localhost:5070/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt":"Which segment has the lowest retention?",
    "model":"claude-haiku-4.5",
    "systemMessage":"You are a retail analytics assistant. Context: 4 segments — High Value (92% retention), Regular (78%), At Risk (45%), New (65%). Answer in one sentence."
  }'
```

Expected behaviour: a grounded answer naming **At Risk** at 45%. Without that
context, the model has no direct access to your seed data. Lab 03 replaces
static context with a tool the model can call only when it needs retail facts.

## Step 9 — Know the basic session calls

The Python SDK objects support `async with`, so samples clean up
deterministically for both the client and session.

For non-streaming one-shot prompts, the SDK also exposes:

```python
await session.send_and_wait(prompt, timeout=60.0)
```

The FastAPI service uses `send(prompt)` because it processes every delta as it
arrives.

## Step 10 — Try the UI path

Back in the browser at <http://localhost:5070>, choose a model, ask
*"Name three retail KPIs. One line each."*, and watch the message render chunk
by chunk. If the stream fails, inspect the `data: {"error": "..."}` frame.

The finished exchange looks like this — the same SSE frames you read with `curl`
above, parsed by `app.js` and rendered as Markdown:

![The chat UI after asking "Name three retail KPIs. One line each." The
assistant has replied with a numbered list: Conversion Rate, Average Order Value
(AOV), and Customer Retention Rate, each with a one-line
definition.](../../screenshots/python-chat-ui-response.png)

💡 Mid-stream the assistant bubble shows an animated typing indicator; it is
replaced by the rendered Markdown once the `[DONE]` sentinel arrives.

⚠️ The static UI posts `{ prompt, model }` from `app/static/app.js`, matching
`ChatRequest`. An earlier revision sent `message` instead; because Pydantic
ignores unknown keys rather than rejecting them, the browser streamed a reply to
an empty prompt and nothing failed loudly. `tests/test_chat_contract.py` now
asserts the field `app.js` sends is the field the API reads.

## ✅ Checkpoint

You can now explain:

- [x] The SSE wire format and why the blank line matters
- [x] Why errors are streamed rather than returned as HTTP status codes
- [x] How FastAPI's `StreamingResponse` wraps the SDK stream
- [x] Why Python branches on `evt.type` instead of event subclasses
- [x] Why models are discovered at runtime
- [x] How a system message grounds the assistant in the retail domain

## 💡 Extra credit

Open `app/services/copilot_chat.py` and temporarily log every event type before
the `if` chain. Send one short prompt and compare the event sequence with the
helper sample:

```bash
uv run python -m sdk_labs events
```

That deeper event lifecycle sample is
[`sdk_labs/events_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py).

## Related

- Previous: [Lab 01 — Setup](../01-setup/)
- Next: [Lab 03 — Tools](../03-tools/)
- [Demo: Copilot SDK integration](../../demos-python/01-copilot-sdk-integration.md)
