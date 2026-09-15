# ラボ 04 — イベント

**目的:** Copilot SDK のセッションイベントのライフサイクルを理解します。具体的には、SDK が実際に何を発行するのか、イベントがどの順序で到着するのか、そしてストリーミング、テレメトリ、完了、エラーなどの一般的な処理でどのイベントが重要なのかを把握します。

**所要時間:** 約20分です。

**前提条件:** [ラボ 03](../03-tools/) を完了していること。

## ステップ 1 — イベントのサンプルを実行する

`src/AgentOrchestrator-python` から SDK のラボサンプルを実行します。

```bash
cd src/AgentOrchestrator-python
uv run python -m sdk_labs events
```

モデルを上書きするには `--model <id>` を付けます。

```bash
uv run python -m sdk_labs events --model gpt-5-mini
```

想定される出力は次のとおりです。

```text
== Lab 04: events ==

Model: claude-haiku-4.5
Prompt: Name two retail KPIs. One line each.

  1. session.start
  2. pending_messages.modified
  3. session.skills_loaded
  4. system.message
  5. session.tools_updated
  6. user.message
  7. hook.start
  8. session.title_changed
  9. hook.end
 10. assistant.turn_start
 11. session.usage_info
 12. model.call_start
 13. assistant.streaming_delta
 14. assistant.reasoning_delta
 15. assistant.streaming_delta
 16. assistant.reasoning_delta
 17. assistant.streaming_delta
 18. assistant.reasoning_delta
 19. assistant.streaming_delta
 20. assistant.reasoning_delta
 21. assistant.streaming_delta
 22. assistant.reasoning_delta
 23. assistant.streaming_delta
 24. assistant.reasoning_delta
 25. assistant.streaming_delta
 26. assistant.message_start
 27. assistant.streaming_delta
 28. assistant.streaming_delta
 29. assistant.usage
 30. assistant.message
     content: 1. **Sales per Square Foot** — Revenue generated per unit of retail floor space;…
     (preceded by 3 delta events)
 31. assistant.reasoning
 32. assistant.turn_end
 33. hook.start
 34. hook.end
 35. session.usage_checkpoint
 36. assistant.idle
 37. session.idle

Total delta events: 3
 38. session.shutdown
 39. session.background_tasks_changed
 40. session.background_tasks_changed
```

注目すべきなのは、その量です。単純な 1 回のプロンプトのやり取りでも、「ユーザーメッセージ、アシスタントメッセージ、完了」よりはるかに多くのイベントが発行されます。

⚠️ **イベント 38〜40 は集計行の後に到着します。** `Total delta events: 3` はセッションがアイドル状態を報告した時点で出力されますが、`async with session:` ブロックはまだ終了していません。終了処理の過程でさらに 3 個のイベントが発行されます。これは、*アイドル状態と終了済みは同じではない*ことを示す重要な注意点です。

⚠️ **上の番号は 1 回の観測結果であり、契約ではありません。** 正確な件数や順序はモデル、プロンプト、SDK のバージョンによって変わります。固定仕様としてではなく、全体の形を理解するために読んでください。

## ステップ 2 — ライフサイクルの各段階をたどる

イベントストリームは、段階ごとにまとめると理解しやすくなります。

1. **セッションの準備（1〜5）** — セッションが開始され、保留中のメッセージとスキルが読み込まれ、システムメッセージが現れ、`session.tools_updated` によってツールが通知されます。
2. **ユーザーのターン（6〜9）** — ユーザーメッセージが受理され、フックイベントが一連の処理の中で実行され、セッションタイトルが変わる場合があります。
3. **アシスタントターンの開始（10〜12）** — アシスタントのターンが始まり、使用量情報が現れ、モデル呼び出しが開始されます。
4. **ストリーミング（13〜28）** — ストリーミングのデルタと推論のデルタが到着し、その後に `assistant.message_start` が続きます。
5. **完了（29〜32）** — アシスタントの使用量が報告され、最終的なアシスタントメッセージが届き、推論が確定し、アシスタントのターンが終了します。
6. **終了処理とアイドル状態（33〜37）** — 別の一対のフックが実行され、使用量のチェックポイントが記録されます。アシスタントがアイドル状態になり、その後セッション全体もアイドル状態になります。
7. **終了（38〜40）** — `async with session:` の終了処理中に発行されます。

フックイベントは、同じ順序付きストリームの一部です。ガバナンスフックを調べている場合、この順序は重要です。`hook.start` と `hook.end` は別チャネルではなく、実際の処理の前後に現れるためです。詳しくは [追加ラボ — ガバナンスフック](../../labs/extra-governance-hooks/) と [フックとガバナンス](../../breakouts/hooks-and-governance.md) を参照してください。

使用量にも専用のイベントがあります。`session.usage_info`、`assistant.usage`、`session.usage_checkpoint` です。テキスト内容ではなく、トークンやコストのテレメトリを確認したい場合は、これらのイベントに注目してください。

## ステップ 3 — `session.on` で購読する

[`events_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py)
を開き、購読処理を確認します。

```python
            waiter = IdleWaiter()
            counters = {"order": 0, "deltas": 0}

            def on_event(evt: SessionEvent) -> None:
                # Deltas arrive in a flood; count them instead of printing each one.
                if evt.type is SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    counters["deltas"] += 1
                    return

                counters["order"] += 1
                # Unlike C#, the event type is a value on the event rather than
                # a subclass, so this prints evt.type instead of a class name.
                print(f"{counters['order']:3d}. {evt.type.value}")

                if evt.type is SessionEventType.ASSISTANT_MESSAGE:
                    print(f"     content: {trim(evt.data.content)}")
                    print(f"     (preceded by {counters['deltas']} delta events)")
                elif evt.type is SessionEventType.SESSION_ERROR:
                    print(f"     ERROR: {evt.data.message}")

                waiter.handle(evt)

            session.on(on_event)
```

このラボプロジェクトでは、PyPI の `github-copilot-sdk` **1.0.9** にバージョンを固定し、`copilot` からインポートしています。また、Python 3.11 以降が必要です。

⚠️ **これは .NET SDK との最大の構造的な違いです。** C# では各イベントがそれぞれ独立したクラスであり、そのサブクラスに対してパターンマッチします。

```csharp
// .NET — one class per event
session.On<SessionEvent>(evt => Console.WriteLine(evt.GetType().Name));
```

Python には `SessionEvent` データクラスが **1 つだけ**あります。イベントの種類は、そのオブジェクトの*型*ではなく*値*として表現されます。

そのため、この実行記録では .NET ラボの `AssistantMessageEvent`（クラス名）ではなく、`assistant.message`（列挙型の `.value`）が表示されます。比較には `is` を使ってください。`SessionEventType` の各メンバーは単一のインスタンスです。

`SessionEvent` には `data`、`id`、`timestamp`、`type`、`agent_id`、`ephemeral`、`parent_id`、`raw_type` が含まれます。`evt.data` の形式は `evt.type` に依存するため、このサンプルでは `ASSISTANT_MESSAGE` の分岐内でだけ `evt.data.content` を読んでいます。

💡 `session.on(handler)` は**購読解除用の呼び出し可能オブジェクトを返します**。セッションが終了する前に監視を止める必要がある場合は保持してください。たとえば `session.on(on_event)` の戻り値を保存して、あとで呼び出します。

## ステップ 4 — 実アプリのハンドラーと比較する

ライフサイクルを学べるように、このサンプルはほぼすべてをログに出します。しかし実際のアプリでは、そこまで多くは必要ありません。

[`copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py)
を開いてハンドラーを見てください。反応しているのは 4 種類のイベントだけです。

```python
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

これは本番向けとして妥当な選択です。ブラウザーへのストリーミングでアプリに必要なのは、テキストの断片、最終メッセージのログ出力、完了通知、エラー処理です。準備、フック、推論、テレメトリのすべてのイベントで分岐する必要はありません。

2 つの仕組みが連携している点に注目してください。テキストの断片は `asyncio.Queue` に入るので即座にストリーミングできます。一方、アイドル状態とエラーは `Future` を完了させ、ジェネレーターがいつ停止すべきかを伝えます。この分担は [Demo 01](../../demos-python/01-copilot-sdk-integration.md) の主題です。

⚠️ **デルタには 2 系統あります。**
`assistant.streaming_delta` と `assistant.message_delta` は同じイベントではありません。このサンプルが抑制しているのは `ASSISTANT_MESSAGE_DELTA` だけなので、上の実行記録ではデルタ数として `Total delta events: 3` が表示される一方で、多数の `assistant.streaming_delta` 行も見えています。誤ったほうを購読すると、期待よりもずっと少ないデータの断片しか見えない場合があります。名前だけで同じだと決めつけず、自分のシナリオで実際に何が発行されるかを測定してください。

## ステップ 5 — アイドル状態で完了し、エラーで失敗させる

`session.idle` は、サンプルとアプリが使っている完了シグナルです。イベントは**プッシュ専用のコールバック**であり、`await` できる非同期イテレーターはありません。そのため、コールバックによって完了する `Future` が必要です。サンプルでは共通の [`IdleWaiter`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py) を使います。

```python
class IdleWaiter:
    """Resolves when the session reports idle, or raises on session error."""

    def __init__(self) -> None:
        self._future: asyncio.Future[None] = asyncio.get_event_loop().create_future()

    def handle(self, evt: SessionEvent) -> bool:
        """Returns True when the event was a terminal (idle/error) event."""
        if evt.type is SessionEventType.SESSION_IDLE:
            if not self._future.done():
                self._future.set_result(None)
            return True
        if evt.type is SessionEventType.SESSION_ERROR:
            if not self._future.done():
                self._future.set_exception(RuntimeError(evt.data.message))
            return True
        return False

    async def wait(self) -> None:
        await asyncio.wait_for(self._future, timeout=TIMEOUT_SECONDS)
```

イベントのサンプルでは、上のコールバックが各イベントに対して `waiter.handle(evt)` を呼びます。プロンプトを送ったあと、集計を表示する前に `waiter.wait()` の完了を待ちます。

これは、C# の `TaskCompletionSource` に相当する Python 側の仕組みです。

⚠️ **エラーイベントは必ず処理してください。** セッションが失敗しても例外を設定する処理がなければ、`await waiter.wait()` はタイムアウトするまで待ち続けます。正常系は問題なく動くため、この失敗モードは見落としやすいです。

⚠️ **タイムアウトは必ず設定してください。** `IdleWaiter.wait()` は Future を `asyncio.wait_for(..., timeout=180)` で包んでいます。トランスポートが切断されるとアイドル通知もエラーも来ない可能性があり、タイムアウトがなければコルーチンは永久に停止しません。

💡 応答だけが必要で、ライフサイクルに関心がない場合、SDK にはこの待機を代行する簡便な方法があります。
`await session.send_and_wait(prompt, timeout=180)` です。

## ⚠️ 落とし穴

- `SessionEvent` データクラスは 1 つだけなので、サブクラスではなく `evt.type` で分岐してください。
- `assistant.streaming_delta` と `assistant.message_delta` は別のイベントです。
- アイドル状態は終了済みを意味しません。`async with` ブロックの終了処理中にもイベントは到着します。
- すべてのイベントをログに出すのは学習には有用ですが、アプリのコードとしてはノイズが多くなります。
- assistant message だけを待つのでは不十分です。`session.idle` で完了させてください。
- `session.error` を無視すると、呼び出し元はタイムアウトするまで待たされます。
- ハンドラーは *SDK から* 呼び出されるため、重い処理をその場で実行せず、高速に保ってキューに仕事を渡してください。

## 💡 追加課題

1. サンプルを変更して、`evt.type.value` が `tool.` で始まるツール関連のイベントだけを表示してください。
2. `session.send(...)` の前に `time.perf_counter()` を記録し、関心のある最初の delta で止めて、time-to-first-token を測定してください。
3. 使用量関連のイベントを別に数え、どこに現れるかをログに出してください。
4. 単純な番号付き一覧ではなく、上で説明した 7 つのライフサイクル段階にイベントを分類してください。
5. `evt.raw_type` を `evt.type.value` と並べて出力し、両者がどこで異なるかを確認してください。

## ✅ チェックポイント

ここまでで、次の内容を説明できるようになります。

- [x] SDK が発行する順序付きのセッションライフサイクル
- [x] Python が C# と異なり、`evt.type` 列挙型を持つ 1 つの `SessionEvent` を使う理由
- [x] `session.on` が購読解除用の呼び出し可能オブジェクトを返すこと
- [x] 実アプリが発行されたイベント全部ではなく、その一部だけを扱う理由
- [x] `streaming_delta` と `message_delta` の違い
- [x] `session.idle` が処理完了を意味する理由と、idle ≠ closed である理由
- [x] エラーイベントが待機中の Future を失敗させる必要がある理由と、タイムアウトが重要な理由
- [x] フックイベントと使用量イベントがライフサイクルのどこに現れるか

## 関連資料

- 前へ: [ラボ 03 — ツール](../03-tools/)
- 次へ: [ラボ 05 — セッション](../05-sessions/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
- [追加ラボ — ガバナンス フック](../../labs/extra-governance-hooks/)
- [フックとガバナンス](../../breakouts/hooks-and-governance.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
