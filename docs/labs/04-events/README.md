# ラボ 04 — イベント

**目標:** Copilot SDK セッションイベントのライフサイクルを理解します。SDK が実際に発行する内容、
イベントが到着する順序、およびストリーミング、テレメトリ、完了、エラーなどの一般的な処理で
重要となるイベントを確認します。

**所要時間:** 約20分

**前提条件:** [ラボ 03](../03-tools/)を完了していること。

## 手順 1 — イベントサンプルを実行する

リポジトリルートから SDK ラボのサンプルを実行します。

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- events
```

想定される出力:

```
== Lab 04: events ==

Model: claude-haiku-4.5
Prompt: Name two retail KPIs. One line each.

  1. SessionStartEvent
  2. SessionManagedSettingsResolvedEvent
  3. PendingMessagesModifiedEvent
  4. SessionSkillsLoadedEvent
  5. SystemMessageEvent
  6. SessionToolsUpdatedEvent
  7. UserMessageEvent
  8. HookStartEvent
  9. SessionTitleChangedEvent
 10. HookEndEvent
 11. AssistantTurnStartEvent
 12. SessionUsageInfoEvent
 13. ModelCallStartEvent
 14. AssistantStreamingDeltaEvent
 15. AssistantReasoningDeltaEvent
 16. AssistantStreamingDeltaEvent
 17. AssistantReasoningDeltaEvent
 18. AssistantStreamingDeltaEvent
 19. AssistantReasoningDeltaEvent
 20. AssistantStreamingDeltaEvent
 21. AssistantReasoningDeltaEvent
 22. AssistantStreamingDeltaEvent
 23. AssistantReasoningDeltaEvent
 24. AssistantStreamingDeltaEvent
 25. AssistantReasoningDeltaEvent
 26. AssistantStreamingDeltaEvent
 27. AssistantMessageStartEvent
 28. AssistantStreamingDeltaEvent
 29. AssistantStreamingDeltaEvent
 30. AssistantUsageEvent
 31. AssistantMessageEvent
     content: 1. **Conversion Rate** — The percentage of store visitors or website traffic tha…
     (preceded by 3 delta events)
 32. AssistantReasoningEvent
 33. AssistantTurnEndEvent
 34. HookStartEvent
 35. HookEndEvent
 36. SessionUsageCheckpointEvent
 37. AssistantIdleEvent
 38. SessionIdleEvent

Total delta events: 3
```

注目すべき点はイベントの多さです。1つのプロンプトによる単純なやり取りでも、
「ユーザーメッセージ、アシスタントメッセージ、完了」よりはるかに多くのイベントが発行されます。

⚠️ サンプルは `AssistantMessageDeltaEvent` を別に数え、それらのイベントを出力しません。
イベント一覧に多数の `AssistantStreamingDeltaEvent` が表示されていても、
`Total delta events: 3` と表示されるのはこのためです。

⚠️ **上記の数値は1回の実行で観測された結果であり、入出力の契約ではありません。** 一覧には
*出力された*イベントが38件あります。さらに3件を受信しましたが出力を抑制したため、到着した
イベントは合計41件です。正確な件数と順序はモデル、プロンプト、SDK バージョンによって異なります。
この並びは固定仕様ではなく、全体の流れを理解するために使用してください。

## 手順 2 — ライフサイクルの各フェーズを確認する

イベントストリームは、次のフェーズに分けると理解しやすくなります。

1. **セッションのセットアップ (1〜6)** — セッションが開始し、管理対象の設定が解決され、
    保留中のメッセージとスキルが読み込まれます。システムメッセージが現れ、
    `SessionToolsUpdatedEvent` でツールが通知されます
2. **ユーザーターン (7〜10)** — ユーザーメッセージが受理され、フックイベントが
    同じイベントストリーム内（インバンド）で実行されます。セッションタイトルが変更されることもあります
3. **アシスタントターンの開始 (11〜13)** — アシスタントターンが開始し、使用量情報が公開され、
    モデル呼び出しが始まります
4. **ストリーミング (14〜29)** — ストリーミングと推論の差分が到着し、
    続いて `AssistantMessageStartEvent` が発行されます
5. **完了 (30〜33)** — アシスタントの使用量が報告され、最終アシスタントメッセージが到着し、
    推論が確定して、アシスタントターンが終了します
6. **終了処理とアイドル (34〜38)** — もう1組のフックが実行され、使用量のチェックポイントが記録されます。
    アシスタントがアイドル状態になり、続いてセッション全体がアイドル状態になります

フックイベントは、同じ順序付きストリームの一部です。ガバナンスフックを調べる場合、この順序が重要です。
`HookStartEvent` と `HookEndEvent` は別のサイドチャネルではなく、処理を挟む形で現れます。
関連するデモ資料については、[追加 — ガバナンスフック](../extra-governance-hooks/)と
[フックとガバナンス](../../breakouts/hooks-and-governance.md)を参照してください。

使用量にも固有のイベントがあります。`SessionUsageInfoEvent`、`AssistantUsageEvent`、
`SessionUsageCheckpointEvent` です。テキスト内容ではなくトークンやコストのテレメトリを
確認する場合は、これらのイベントを調べます。

## 手順 3 — v1 パターンで購読する

[`EventsSample.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/EventsSample.cs)
を開き、購読処理を探します。

```csharp
session.On<SessionEvent>(evt =>
{
    Console.WriteLine(evt.GetType().Name);
});
```

⚠️ **明示的な `<SessionEvent>` が重要です。** GitHub Copilot SDK v1.x では、
非ジェネリック形式から型引数が推論されなくなりました。

```csharp
session.On(evt => { });
```

この古い v0.x の形式は、v1.x では `CS0411` で失敗します。古いサンプルをコピーして
このコンパイラエラーが表示された場合は、明示的な型引数を追加してください。

古いコードを更新する場合は、名前空間も確認してください。SDK v1.0.0 では
`GitHub.Copilot.SDK` から次の名前空間へ移動しました。

```csharp
using GitHub.Copilot;
```

## 手順 4 — アプリが処理するイベントと比較する

ライフサイクルを学べるように、サンプルはほぼすべてをログに記録します。実際のアプリでは、
そのすべてを処理する必要はありません。

[`CopilotChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs)
を開き、イベントの `switch` を確認します。処理するイベント型は次の4つだけです。

```csharp
case AssistantMessageDeltaEvent delta:
    outputChannel.Writer.TryWrite(delta.Data.DeltaContent ?? "");
    break;
case AssistantMessageEvent msg:
    _logger.LogInformation("Assistant response complete: {Length} chars",
        msg.Data.Content?.Length ?? 0);
    break;
case SessionIdleEvent:
    done.SetResult();
    break;
case SessionErrorEvent error:
    done.SetException(new Exception(error.Data.Message));
    break;
```

これは妥当な運用環境向けの選択です。ブラウザーへのストリーミングに必要なのは、テキストチャンク、
最終メッセージのログ、完了シグナル、エラーパスです。セットアップ、フック、推論、テレメトリの
すべてのイベントを `switch` で処理する必要はありません。

⚠️ 差分イベントには、`AssistantStreamingDeltaEvent` と `AssistantMessageDeltaEvent` という
異なる2つの系統があります。この実行では多数の `AssistantStreamingDeltaEvent` が現れましたが、
サンプルが数えた `AssistantMessageDeltaEvent` は2件だけでした。目的に合わないイベントを購読すると、
想定よりはるかに少ないチャンクしか得られない可能性があります。名前が同じ意味だと想定する前に、
実際のシナリオで何が発行されるかを測定してください。

## 手順 5 — アイドル時に完了し、エラー時に失敗させる

`SessionIdleEvent` は、サンプルとアプリが使用する完了シグナルです。一般的なパターンでは、
セッションがアイドル状態になったときに `TaskCompletionSource` を完了させます。

```csharp
var done = new TaskCompletionSource();

session.On<SessionEvent>(evt =>
{
    switch (evt)
    {
        case SessionIdleEvent:
            done.TrySetResult();
            break;
        case SessionErrorEvent error:
            done.TrySetException(new Exception(error.Data.Message));
            break;
    }
});

await session.SendAsync(new MessageOptions { Prompt = prompt });
await done.Task;
```

⚠️ `SessionErrorEvent` は必ず処理してください。セッションが失敗したときに
`TaskCompletionSource` へ例外を設定しないと、`await done.Task` が永遠に待機する可能性があります。
正常系は問題なく動作するため、この障害モードは見落としやすい点に注意してください。

## ⚠️ 注意点

- `session.On(evt => ...)` は古い形式です。SDK v1.x では
  `session.On<SessionEvent>(evt => ...)` を使用します
- `GitHub.Copilot.SDK` を使用する古い名前空間は `GitHub.Copilot` に変更する必要があります
- `AssistantStreamingDeltaEvent` と `AssistantMessageDeltaEvent` は異なるイベント型です。
  測定せずに同じものとして扱わないでください
- すべてのイベントのログは学習には有用ですが、アプリコードでは大量の出力になります
- アシスタントメッセージを待つだけでは不十分です。`SessionIdleEvent` で処理を完了してください
- `SessionErrorEvent` を無視すると、呼び出し元が永遠に待機する可能性があります

## 💡 発展課題

次の小さな実験のいずれかを試してください。

1. イベント名に `Tool` を含むものや、ツール処理を挟むフックイベントなど、ツール関連のイベントだけを
    出力するようにサンプルを変更する
2. `SendAsync(...)` の前に `Stopwatch` を開始し、対象とする最初の差分イベントで停止して、
    最初のトークンが到着するまでの時間を測定する
3. 使用量関連のイベントを別に数え、ライフサイクルのどこに現れるかをログに記録する
4. 番号付きの平坦な一覧を出力する代わりに、イベントを上記6つのライフサイクルフェーズにまとめる
    フィルターを追加する

## ✅ チェックポイント

ここまでで、次の項目を説明できるようになりました。

- [x] SDK が発行する順序付きセッションライフサイクル
- [x] v1.x で `On<SessionEvent>` に明示的な型引数が必要な理由
- [x] 実際のアプリが通常、発行される全イベントの一部だけを処理する理由
- [x] すべてのイベントを観測することと、有用なチャンクをストリーミングすることの違い
- [x] `SessionIdleEvent` が処理を完了させる理由
- [x] `SessionErrorEvent` によって待機中のタスクを失敗させる必要がある理由
- [x] ライフサイクル内でフックイベントと使用量イベントが現れる位置

## 関連資料

- 前へ: [ラボ 03 — ツール](../03-tools/)
- 次へ: [ラボ 05 — セッション](../05-sessions/)
- [デモ: Copilot SDK の統合](../../demos/01-copilot-sdk-integration.md)
- [フックとガバナンス](../../breakouts/hooks-and-governance.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
