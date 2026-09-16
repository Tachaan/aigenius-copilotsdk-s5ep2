# Copilot SDK の組み込み

このウォークスルーでは、FastAPI アプリが GitHub Copilot SDK をどのように組み込み、Copilot セッションをアプリケーションサービスとして扱っているかを説明します。SDK クライアントの起動、ストリーミングセッションの作成、セッションイベントの監視、コールバックから非同期ジェネレーターへの橋渡し、古いモデルカタログを避ける方法を順に確認します。

## SDK を使っている場所

主な統合箇所は [`app/services/copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py) です。このファイルでは、次のように SDK をインポートしています。

```python
from copilot import CopilotClient, SessionEvent, SessionEventType
```

PyPI パッケージ名は `github-copilot-sdk` で、[`pyproject.toml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/pyproject.toml) では **1.0.9** に固定されていますが、インポート時のルート名は `copilot` です。

```python
requires-python = ">=3.11"
dependencies = [
    "github-copilot-sdk==1.0.9",
```

Python 3.11 以降が必要です。

## 継続利用する単一サービス

[`app/main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py) では、FastAPI アプリのライフタイム全体で使うチャットサービスを 1 つ作成します。

```python
app.state.chat_service = CopilotChatService()
```

このサービスは必要になった時点で接続します。`ensure_started()` は `asyncio.Lock` で保護されているため、複数の HTTP リクエストが同時に到着しても、競合して 2 つのトランスポートを起動することはありません。

```python
self._lock = asyncio.Lock()
```

```python
async with self._lock:
    if self._is_started and self._client is not None:
        return
```

起動と停止は明示的に行われます。

```python
self._client = CopilotClient()
await self._client.start()
self._is_started = True
```

```python
if self._client is not None:
    await self._client.stop()
```

SDK は短命なスクリプト向けに `async with CopilotClient()` もサポートしています。ラボのサンプルでは、クライアントが 1 つのコマンド実行中だけ存在すればよい場合にこの形式を使っています。

## ストリーミングセッションの作成

`CopilotChatService.chat_stream()` は、各プロンプトごとに新しい SDK セッションを作成します。

```python
session = await self._client.create_session(
    model=model,
    streaming=True,
    system_message=(
        {"mode": "append", "content": system_message} if system_message else None
    ),
)
```

`create_session(...)` の引数はキーワード専用です。重要なパラメーターは `model`、`streaming`、`system_message`、`tools`、`mcp_servers`、`session_id`、`on_permission_request` です。

`system_message` は複数の `TypedDict` 型を組み合わせたユニオン型です。

```python
{"mode": "append", "content": "..."}
{"mode": "replace", "content": "..."}
```

このデモでは追加モードを使い、Copilot の基本動作を置き換えずにアプリケーション側の文脈を加えています。

⚠️ Python のカスタムツールでは `on_permission_request` が必須で、これがないと呼び出しは拒否されます。.NET サンプルでは、同じ単純なツールの処理にこのハンドラーは不要です。また Python では、`copilot.rpc` の権限判定を使うために `GHCP001` の試験的 API に関する警告を抑制する必要もありません。

## セッションイベント

アーキテクチャ上の要点は、Python SDK のイベントが **プッシュ専用のコールバック** であることです。`session.on(handler)` はハンドラーを登録し、購読解除用の呼び出し可能オブジェクトを返します。非同期イテレーターはありません。

C# SDK とは異なり、Python で公開される `SessionEvent` データクラスは **1 種類だけ**です。イベントごとにサブクラスをパターンマッチするのではなく、`SessionEventType` 列挙型である `evt.type` で分岐します。実際のハンドラーは次のとおりです。

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

`ASSISTANT_MESSAGE_DELTA` はストリーム中のテキストを運び、`ASSISTANT_MESSAGE` は応答全体の完了を示します。`SESSION_IDLE` は `Future` を完了させて待機を終え、`SESSION_ERROR` は失敗を表面化させます。

## コールバックを非同期ジェネレーターに橋渡しする

FastAPI のストリーミングには非同期イテレーターが必要ですが、SDK はハンドラーを呼び出す方式です。そのため、このサービスではコールバックから `asyncio.Queue` へデータを渡し、`chat_stream()` で取り出しています。

```python
queue: asyncio.Queue[object] = asyncio.Queue()
loop = asyncio.get_running_loop()
```

```python
item = await queue.get()
if item is _DONE:
    break
if isinstance(item, BaseException):
    raise item
yield item  # type: ignore[misc]
```

`_DONE` はコンテンツの値ではなく、完了を示すセンチネルオブジェクトです。

```python
# Sentinel pushed onto the queue when the session goes idle.
_DONE = object()
```

```python
queue.put_nowait(_DONE)
```

キューが必要なのは、イベントコールバックから HTTP レスポンスへ直接 `yield` できないためです。これは、C# サービスが `System.Threading.Channels` のチャネルに書き込む構成に対応しています。

## 再接続の挙動

SDK のトランスポートが失われた場合、サービスはクライアントを異常状態として扱い、その例外をキュー経由で渡します。

```python
except (ConnectionError, OSError) as ex:
    logger.warning("Copilot connection lost: %s", ex)
    self._is_started = False
    queue.put_nowait(ex)
```

処理中のリクエストは失敗し、次のリクエストで再び `ensure_started()` が呼ばれます。`_is_started` が false であるため、古いクライアントは停止され、新しいトランスポートが確立されます。

## 利用可能なモデルの動的な一覧取得

`CopilotChatService.list_models()` は、接続済みの Copilot CLI に対して、サインイン中のアカウントで利用可能なモデルを問い合わせます。

```python
models = await self._client.list_models()
return [(m.id, m.name or m.id) for m in models or [] if m.id]
```

SDK は `.id` と `.name` を持つ `ModelInfo` オブジェクトを返します。利用可能性はアカウントやロールアウト状況によって変わるため、モデル ID をハードコードするのは危険です。

既知の上流側の不具合が 1 つあります。`list_models()` は `ValueError: Missing required field 'multiplier' in ModelBilling` を送出することがあります（[github/copilot-sdk#1302](https://github.com/github/copilot-sdk/issues/1302)）。[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py) では例外をまとめて捕捉し、6 つのモデルから成る静的カタログにフォールバックします。

```python
except Exception:
    # Includes the known SDK issue where ModelBilling is missing the
    # required 'multiplier' field: github/copilot-sdk#1302.
    logger.warning(
        "Could not list models from Copilot CLI; using static catalog", exc_info=True
    )

return list(AVAILABLE_MODELS.values())
```

これにより、ライブ検出が一時的に壊れていてもモデル選択 UI を利用可能な状態に保てます。

## 関連項目

- [SSE によるストリーミング応答](./02-sse-streaming.md)
- [小売ドメイン](./03-retail-analytics.md)
- [ブラウザー UI](./04-web-ui.md)
- ソース: [`copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py), [`chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py), [`main.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py), [`events_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py), [`tools_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/tools_sample.py), [`pyproject.toml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/pyproject.toml)
