# SSE によるストリーミング応答

このウォークスルーでは、FastAPI ルーターからブラウザークライアントまでチャット応答が流れる経路を追います。SSE の正確な通信形式、`StreamingResponse` の使い方、Python スタックが .NET API と同じエラー処理の契約を含む通信上の契約を意図的に維持している理由を説明します。

## API のエントリーポイント

[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py) は `POST /api/chat/stream` を処理します。`ChatRequest` を受け取り、要求されたモデル、または既定の `claude-haiku-4.5` を選択し、FastAPI の `StreamingResponse` を返します。

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

これらのヘッダーは、プロキシなどの中継コンポーネントやブラウザーに対して、これは完了までバッファリングすべき通常の JSON 応答ではなく、長時間継続するストリームであることを伝えます。

## 通信形式

[`CopilotChatService.chat_stream`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py) から届くデータの各断片を、ルーターは小さな JSON オブジェクトにシリアライズし、1 つの SSE メッセージとして書き込みます。

```python
yield f"data: {json.dumps({'content': chunk})}\n\n"
```

ストリームが正常に終了すると、エンドポイントは完了を示すセンチネルを書き込みます。

```python
yield "data: [DONE]\n\n"
```

ストリーム開始後に例外が発生した場合、ルーターは同じ SSE データチャネルにエラーイベントを書き込みます。

```python
yield f"data: {json.dumps({'error': str(ex)})}\n\n"
```

この時点では、HTTP エラーステータスへ確実に切り替えることはできません。ステータスコードとレスポンスヘッダーはすでに送信済みであるため、あとから発生した失敗を報告するには、ストリームのペイロードに埋め込むしかありません。

## 意図的な .NET 互換性

通信上の契約は .NET API と一致しています。つまり、`data: {...}\n\n` のフレームが並び、最後に `data: [DONE]\n\n` で終わります。JSON の空白は Python の `json.dumps` と .NET の `JsonSerializer` で異なる場合がありますが、`content` / `error` のエラーを含むペイロード形式と完了を示すセンチネルは同じです。Python 側では、FastAPI が API と UI の両方を 1 プロセスで配信するため、ポートを **5070** にしています。

## リクエスト本文のエイリアス

`ChatRequest` は Pydantic の camelCase エイリアス生成機能を使っています。

```python
model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

prompt: str | None = None
model: str | None = None
system_message: str | None = None
```

これにより、Python コードは慣用的な形（`system_message`）を保ちながら、.NET クライアントやドキュメントで使われる HTTP 契約（`systemMessage`）を維持できます。

## 切断時の処理

ジェネレーターの内部では、ルーターは次のフレームを書き込む前に、ブラウザー側がすでに切断していないか確認します。

```python
async for chunk in service.chat_stream(prompt, model, body.system_message):
    if await request.is_disconnected():
        break
    yield f"data: {json.dumps({'content': chunk})}\n\n"
```

タブが閉じられた場合やリクエストが放棄された場合でも、API には書き込みを停止してストリーミング処理を巻き戻す経路があります。

## 応答をまとめて返すチャットと正常性確認

同じルーターは、応答全体をまとめて返す `POST /api/chat` と、SDK のトランスポートを必要としない正常性確認用の `GET /api/chat/health` を公開しています。

```python
response = await _service(request).chat(body.prompt or "", model, body.system_message)
return ChatResponse(content=response, model=model)
```

実際に確認した正常性確認の出力は次のとおりです。

```json
{"status":"healthy","service":"CopilotChat","availableModels":["claude-haiku-4.5","gpt-4.1","gpt-5","claude-sonnet-4.5","claude-opus-4.5","gemini-2.5-pro"]}
```

## curl で試す

リクエストはポート 5070 に送ってください。curl がレスポンスをバッファリングしないように、`curl -sN` を使います。

```bash
$ curl -sN -X POST http://localhost:5070/api/chat/stream \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"Reply with exactly: streaming works","model":"claude-haiku-4.5"}'

data: {"content": "streaming works"}

data: [DONE]
```

⚠️ フィールド名は `message` ではなく `prompt` です。認識されないキーは無視されるため、ここで入力を誤ると空のプロンプトが黙って送信されます。エラーにはならず、モデルは一般的な挨拶を返します。

実際のアシスタントの文面はモデルやアカウントの状態に依存しますが、重要なのはフレームの形式です。応答が長くなる場合は、完了を示すセンチネルの前に `data:` フレームが増えるだけです。

## ブラウザクライアント

静的 UI は [`app/static/app.js`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js) で同じ `data: ` フレームを読み取ります。ここでは `fetch()`、`res.body.getReader()`、`TextDecoder` を使っており、描画までの完全な経路は [ブラウザー UI](./04-web-ui.md) で扱っています。

## 関連項目

- [Copilot SDK の組み込み](./01-copilot-sdk-integration.md)
- [小売ドメイン](./03-retail-analytics.md)
- [ブラウザー UI](./04-web-ui.md)
- ソース: [`chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py), [`copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py), [`app.js`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js)
