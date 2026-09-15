# ラボ 02 — 最初のストリーミング チャット

**目的:** 1 つのプロンプトが Python スタック全体をどのように流れるかを追います。
経路は HTTP クライアント → FastAPI → Copilot SDK → モデル → 応答です。また、モデルの
検出にハードコードされた一覧ではなく実行時のデータを使う理由を理解します。

**所要時間:** 約20分

**前提条件:** [ラボ 01](../01-setup/) を完了し、FastAPI サーバーがポート 5070 で
動作していること。

## ステップ 1 — サーバーを起動または確認する

リポジトリ ルートから実行します。

```bash
cd src/AgentOrchestrator-python
uv run uvicorn app.main:app --port 5070
```

後で UI を確認したい場合は <http://localhost:5070> を開いてください。同じプロセスが
API と静的 UI の両方を提供します。

API が正常であることを確認します。

```bash
curl http://localhost:5070/api/chat/health
```

期待される出力は次のとおりです。

```json
{"status":"healthy","service":"CopilotChat","availableModels":["claude-haiku-4.5","gpt-4.1","gpt-5","claude-sonnet-4.5","claude-opus-4.5","gemini-2.5-pro"]}
```

このフォールバック一覧は意図的に小さくしてあります。実際のモデル選択 UI は、サインイン中の
Copilot アカウントに対して利用可能なモデルを問い合わせます。

## ステップ 2 — 通信形式を確認する

プロンプトを送信し、加工されていない Server-Sent Events を観察してください。

```bash
curl -sN -X POST http://localhost:5070/api/chat/stream \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"Reply with exactly: streaming works","model":"claude-haiku-4.5"}'
```

取得される出力は次のようになります。

```text
data: {"content": "streaming works"}

data: [DONE]
```

注目すべき点は 3 つあります。各イベントフレームは `data: ` と JSON で構成され、その後に
**空行**が続きます。長い回答はデータの断片が任意の位置で分割されるため、複数のフレームに分かれます。
そしてストリームは、完了を示すセンチネル `data: [DONE]` で終了します。

⚠️ リクエストモデルは `prompt`、`model`、任意の `systemMessage` です。`message` のような
認識されないキーは黙って無視されるため、検証エラーではなく汎用的なあいさつが返ってきます。

## ステップ 3 — サーバー側を見つける

[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py)
を開き、`stream_chat` を見つけてください。

`stream_chat` はメディアタイプが `text/event-stream` の `StreamingResponse` を返します。
`event_stream` の内部では、SDK から届くデータの各断片が SSE フレームとしてシリアライズされます。

```python
yield f"data: {json.dumps({'content': chunk})}\n\n"
```

その後、このルートは完了を示すセンチネル `data: [DONE]` を書き込みます。

⚠️ 空行は飾りではありません。イベントの区切りです。これを取り除くと、
多くの SSE クライアントはイベントの完了を認識できず、バッファリングを続けます。

次に `except` ブロックを見てください。エラーは `data: {"error": "..."}` として
**ストリームの中に**書き込まれます。SSE レスポンスが始まった後では、ステータス行と
ヘッダーはすでに送信済みなので、HTTP 500 はクライアントにとってもはや有用ではありません。

## ステップ 4 — SDK 組み込みを見つける

[`app/services/copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py)
を開いてください。

`CopilotChatService.chat_stream` は、ストリーミングを有効にしたセッションを作成します。

```python
session = await self._client.create_session(
    model=model,
    streaming=True,
    system_message=(
        {"mode": "append", "content": system_message} if system_message else None
    ),
)
```

次にイベントを購読します。

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

このキューは、SDK のコールバック方式と FastAPI の非同期レスポンスジェネレーターをつなぐ橋渡しです。
コールバックはデータの断片を `asyncio.Queue` に積み、ルート側はそのキューを待って SSE フレームを `yield` します。

## ステップ 5 — Python のイベントを理解する

ここが Python と .NET の最初の重要な違いです。

.NET のサンプルでは `AssistantMessageDeltaEvent` や `SessionIdleEvent` のような
イベントのサブクラスをパターンマッチします。Python では、次のようなフィールドを持つ 1 つの
`SessionEvent` データクラスが渡されます。

- `type`
- `data`
- `id`
- `timestamp`

`type` フィールドは `SessionEventType` 列挙型なので、Python コードは次のように分岐します。

```python
if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
    ...
elif evt.type is SessionEventType.SESSION_ERROR:
    ...
```

イベントは**プッシュ専用のコールバック**でもあります。`session.on(handler)` はハンドラーを登録し、購読解除用の呼び出し可能オブジェクトを返します。
直接ループできる非同期イテレーターはありません。

[`sdk_labs/_common.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py)
のヘルパーはこのパターンを使い、`SESSION_IDLE` まで待機するか、`SESSION_ERROR` で例外を送出します。

## ステップ 6 — API に利用可能なモデルを問い合わせる

```bash
curl -s http://localhost:5070/api/chat/models | jq -r '.[].id'
```

`/api/chat/models` は、次のような形式のオブジェクトからなる JSON **一覧**を返します。

```json
{"id":"...","name":"...","description":"..."}
```

このルートは最初に `CopilotChatService.list_models()` を呼び、その中で
`await client.list_models()` を実行します。これにより `.id` と `.name` フィールドを持つ
`ModelInfo` オブジェクトが返されます。

⚠️ `list_models()` には既知の上流側の不具合があり、
`ValueError: Missing required field 'multiplier' in ModelBilling`
を送出することがあります (github/copilot-sdk#1302)。ルーター側は例外をまとめて捕捉し、
静的カタログに切り替えるため、UI では引き続き選択肢を表示できます。

## ステップ 7 — モデルを切り替えて比較する

動的に取得した一覧からモデル ID を 1 つ選んでください。

```bash
MODEL=$(curl -s http://localhost:5070/api/chat/models | jq -r '.[0].id')
echo "Using $MODEL"

curl -sN -X POST http://localhost:5070/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d "{\"prompt\":\"In one sentence, what is customer churn?\",\"model\":\"$MODEL\"}"
```

別の ID でも繰り返し、応答時間、文体、語調を比較してください。

[`sdk_labs/model_picker.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/model_picker.py)
にあるサンプルのモデル選択ロジックも同じ考え方です。`claude-haiku-4.5` を優先しますが、
最終的にはアカウントで実際に使えるモデルに切り替えます。サンプルは
`--model <id>` で上書きできます。

## ステップ 8 — システムメッセージで応答を方向付ける

API は任意の `systemMessage` を受け付けます。サービスはこれを**追加**モードで送るため、
セッションに組み込まれた指示を置き換えるのではなく補足します。

```bash
curl -sN -X POST http://localhost:5070/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt":"Which segment has the lowest retention?",
    "model":"claude-haiku-4.5",
    "systemMessage":"You are a retail analytics assistant. Context: 4 segments — High Value (92% retention), Regular (78%), At Risk (45%), New (65%). Answer in one sentence."
  }'
```

期待される挙動は、根拠に基づいて 45% の **At Risk** を挙げる回答です。この文脈がなければ、
モデルは初期データに直接アクセスできません。ラボ 03 では、この静的な文脈を、
リテールデータが必要なときだけモデルが呼び出せるツールに置き換えます。

## ステップ 9 — 基本的なセッション呼び出しを把握する

Python SDK のオブジェクトは `async with` をサポートしているため、サンプルではクライアントとセッションの両方を
決定的にクリーンアップできます。

ストリーミングしない単発のプロンプトに対しては、SDK は次の呼び出しも提供します。

```python
await session.send_and_wait(prompt, timeout=60.0)
```

FastAPI サービスは、到着した差分を逐次処理するため、`send(prompt)` を使います。

## ステップ 10 — UI 経路を試す

ブラウザーで <http://localhost:5070> に戻り、モデルを選んで
*"Name three retail KPIs. One line each."* と質問し、メッセージがデータの断片ごとに描画される様子を見てください。
ストリームが失敗した場合は、`data: {"error": "..."}` フレームを確認してください。

完了したやり取りは次のようになります。上で `curl` で読んだ SSE フレームを `app.js` が解析し、Markdown として描画したものです。

!["Name three retail KPIs. One line each." と質問した後のチャット UI。assistant は、
Conversion Rate、Average Order Value (AOV)、Customer Retention Rate を、
それぞれ 1 行の定義付き番号付きリストで返しています。](../../screenshots/python-chat-ui-response.png)

💡 ストリーム途中ではアシスタントの吹き出しにアニメーション付きの入力中インジケーターが表示され、
完了を示すセンチネル `[DONE]` が到着すると描画済みの Markdown に置き換わります。

⚠️ 静的 UI は `app/static/app.js` から `{ prompt, model }` を送信し、`ChatRequest` に合わせています。
以前の版では代わりに `message` を送っていましたが、Pydantic は未知のキーを拒否せず無視するため、
ブラウザーは空のプロンプトに対する応答をストリーミングし、目立った失敗にはなりませんでした。
現在は `tests/test_chat_contract.py` で、`app.js` が送るフィールドと API が読むフィールドが一致することを検証しています。

## ✅ チェックポイント

ここまで理解できていれば、次を説明できるはずです。

- [x] SSE の通信形式と、空行が重要な理由
- [x] なぜエラーを HTTP ステータスコードではなくストリームで返すのか
- [x] FastAPI の `StreamingResponse` がどのように SDK のストリームを包むのか
- [x] なぜ Python はイベントのサブクラスではなく `evt.type` で分岐するのか
- [x] なぜモデルは実行時に検出されるのか
- [x] システムメッセージがアシスタントを小売ドメインにどう結び付けるのか

## 💡 追加課題

`app/services/copilot_chat.py` を開き、`if` の連鎖の前で各イベント種別を一時的にログへ出力してください。
短いプロンプトを 1 つ送信し、そのイベントの順序をヘルパーのサンプルと比較してください。

```bash
uv run python -m sdk_labs events
```

より詳しいイベントライフサイクルの例は
[`sdk_labs/events_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py)
にあります。

## 関連資料

- 前へ: [ラボ 01 — セットアップ](../01-setup/)
- 次へ: [ラボ 03 — ツール](../03-tools/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
