# Streaming responses over SSE

This walkthrough follows a chat response from the FastAPI router to the browser client. You will learn the exact SSE wire format, how `StreamingResponse` is used, and why the Python stack deliberately keeps the same contract as the .NET API.

## API entry point

[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py) handles `POST /api/chat/stream`. It accepts a `ChatRequest`, chooses the requested model or the `claude-haiku-4.5` default, and returns a FastAPI `StreamingResponse`:

```python
@router.post("/stream")
async def stream_chat(request: Request, body: ChatRequest) -> StreamingResponse:
```

```python
return StreamingResponse(
    event_stream(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
)
```

Those headers tell intermediaries and the browser that this is a long-lived stream, not a normal JSON response that should be buffered until completion.

## Wire format

For each chunk from [`CopilotChatService.chat_stream`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py), the router serialises a small JSON object and writes one SSE message:

```python
yield f"data: {json.dumps({'content': chunk})}\n\n"
```

When the stream finishes normally, the endpoint writes the sentinel:

```python
yield "data: [DONE]\n\n"
```

If an exception is raised after the stream has started, the router writes an error event in the same SSE data channel:

```python
yield f"data: {json.dumps({'error': str(ex)})}\n\n"
```

At that point it cannot reliably switch to an HTTP error status. The status code and response headers have already been sent, so the only useful way to report a late failure is inside the stream payload.

## Deliberate .NET compatibility

The wire shape is byte-for-byte identical to the .NET API: `data: {...}\n\n` frames terminated by `data: [DONE]\n\n`. That is deliberate, so the same browser client and the same `curl` commands can be used against either stack. The Python page changes the port to **5060**, because FastAPI serves both the API and UI from one process.

## Request body aliases

`ChatRequest` uses Pydantic's camelCase alias generator:

```python
model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

prompt: str | None = None
model: str | None = None
system_message: str | None = None
```

That keeps Python code idiomatic (`system_message`) while preserving the HTTP contract (`systemMessage`) used by the .NET client and docs.

## Disconnect handling

Inside the generator, the router checks whether the browser has gone away before writing the next frame:

```python
async for chunk in service.chat_stream(prompt, model, body.system_message):
    if await request.is_disconnected():
        break
    yield f"data: {json.dumps({'content': chunk})}\n\n"
```

If the tab is closed or the request is abandoned, the API has a path to stop writing and unwind the streaming work.

## Buffered chat and health

The same router exposes `POST /api/chat` for a buffered response and `GET /api/chat/health` for a probe that does not need the SDK transport:

```python
response = await _service(request).chat(body.prompt or "", model, body.system_message)
return ChatResponse(content=response, model=model)
```

Real health output:

```json
{"status":"healthy","service":"CopilotChat","availableModels":["claude-haiku-4.5","gpt-4.1","gpt-5","claude-sonnet-4.5","claude-opus-4.5","gemini-2.5-pro"]}
```

## Try it with curl

Point the request at port 5060. Use `curl -sN` so curl does not buffer the response:

```bash
$ curl -sN -X POST http://localhost:5060/api/chat/stream \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"Reply with exactly: streaming works","model":"claude-haiku-4.5"}'

data: {"content": "streaming works"}

data: [DONE]
```

⚠️ The field is `prompt`, not `message`. An unrecognised key is ignored, so a
typo here silently sends an empty prompt and the model replies with a generic
greeting instead of an error.

The exact assistant text depends on the model and account state, but the frame
shape is the important part. A longer answer simply arrives as more `data:`
frames before the sentinel.

## Browser client

The static UI reads the same `data: ` frames in [`app/static/app.js`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js). It uses `fetch()`, `res.body.getReader()`, and `TextDecoder`; the full rendering path is covered in [The web UI](./04-web-ui.md).

## Related

- [Embedding the Copilot SDK](./01-copilot-sdk-integration.md)
- [The retail domain](./03-retail-analytics.md)
- [The web UI](./04-web-ui.md)
- Source: [`chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py), [`copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py), [`app.js`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js)
