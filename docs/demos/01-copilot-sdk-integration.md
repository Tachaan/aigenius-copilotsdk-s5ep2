# Copilot SDK の組み込み

このウォークスルーでは、API に GitHub Copilot SDK を組み込み、Copilot セッションをアプリケーションサービスとして利用する方法を説明します。アプリが SDK クライアントを起動し、ストリーミングセッションを作成し、セッションイベントを受信し、古くなったモデルカタログを回避する仕組みを確認します。

## SDK を使用する場所

主な統合ポイントは
[`CopilotChatService`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs)
です。SDK は次のようにインポートします。

```csharp
using GitHub.Copilot;
```

この名前空間は、移行時によく問題になる点です。SDK 1.0.0 のリリース前は名前空間が `GitHub.Copilot.SDK` でした。このリポジトリで使用する v1.x では、パッケージ参照名が引き続き `GitHub.Copilot.SDK` であっても、名前空間は `GitHub.Copilot` です。

## プロセス全体で共有する単一クライアント

[`Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs)
では、`CopilotChatService` をシングルトンとして登録します。

```csharp
builder.Services.AddSingleton<CopilotChatService>();
```

このサービスは、API プロセスの存続期間を通じて単一の `CopilotClient` フィールドを保持します。これにより、HTTP リクエストごとに Copilot 接続を開始・停止する必要がなくなり、モデル一覧の取得とチャットストリーミングを1つの管理されたサービスに集約できます。

`CopilotChatService` は `IAsyncDisposable` を実装しています。ホストがシングルトンを破棄すると、`CopilotChatService.DisposeAsync` が `CopilotClient.StopAsync()` を呼び出し、SDK 接続を正常に終了します。

## クライアントの起動と復旧

`CopilotChatService.EnsureStartedAsync` は、モデル一覧の取得やチャットを開始する前のゲートです。

```csharp
if (_isStarted && _client != null) return;

_isStarted = false;
if (_client != null)
{
    try { await _client.StopAsync(); } catch { }
}

_client = new CopilotClient();
await _client.StartAsync();
_isStarted = true;
```

このメソッドは `_isStarted` と `_client` を状態判定の正として扱います。クライアントが起動していない場合や、以前の障害によって異常と判断された場合、サービスは古いクライアントを停止し、新しい `CopilotClient` を作成して起動し、新しい状態を記録します。

復旧処理は `CopilotChatService.ChatStreamAsync` で完了します。バックグラウンドセッションは `IOException` を捕捉し、Copilot 接続が失われたことをログに記録して `_isStarted = false` を設定し、例外を伴って出力チャネルを完了します。次のリクエストでは再び `EnsureStartedAsync` が呼び出され、クライアントが再作成されます。

## ストリーミングセッションの作成

`CopilotChatService.ChatStreamAsync` は、プロンプトごとに `SessionConfig` を構築します。

```csharp
SessionConfig config = new()
{
    Model = model,
    Streaming = true,
    SystemMessage = systemMessage != null ? new SystemMessageConfig
    {
        Mode = SystemMessageMode.Append,
        Content = systemMessage
    } : null
};
```

選択するモデルはリクエストから取得し、サービスの既定値には `claude-haiku-4.5` を使用します。`Streaming = true` を指定すると、SDK は応答の差分を送出します。システムメッセージが指定された場合は、`Append` モードの `SystemMessageConfig` として送信されます。そのため、セッションの基本システム動作を置き換えるのではなく、アプリケーションのコンテキストを追加できます。

セッションは `await using` で作成するため、そのプロンプトの処理が完了すると非同期で破棄されます。

```csharp
await using var session = await _client.CreateSessionAsync(config);
```

## セッションイベント

サービスは、ジェネリック型引数を明示して SDK イベントを購読します。

```csharp
session.On<SessionEvent>(evt => { /* switch on event type */ });
```

v1.x では `<SessionEvent>` の明示が必要です。以前の非ジェネリック形式ではイベント型を確実に推論できなくなったため、型引数の省略はアップグレード時によくある失敗原因です。

`CopilotChatService` は4種類のイベントを処理します。

- `AssistantMessageDeltaEvent` は `DeltaContent` を出力ストリームに書き込みます。
- `AssistantMessageEvent` はアシスタントの応答が完了したことをログに記録します。
- `SessionIdleEvent` は、ターンの完了待ちに使用する `TaskCompletionSource` を完了します。
- `SessionErrorEvent` は SDK エラーをログに記録し、例外を伴って待機タスクを完了します。

購読後、次のようにプロンプトを送信します。

```csharp
await session.SendAsync(new MessageOptions { Prompt = prompt });
```

## SDK イベントと `IAsyncEnumerable` の橋渡し

SDK セッションはバックグラウンドの `Task` 内で実行されます。差分は `Channel<string>` に書き込まれ、外側の非同期イテレーターがそのチャネルを読み取ります。

```csharp
var outputChannel = Channel.CreateUnbounded<string>();

_ = Task.Run(async () =>
{
    // create session, handle events, write chunks
}, cancellationToken);

await foreach (var chunk in outputChannel.Reader.ReadAllAsync(cancellationToken))
{
    yield return chunk;
}
```

この構成には理由があります。C# の非同期イテレーターでは、SDK セッションを所有する `try`/`catch` ブロック内から `yield return` できません。チャネルを使うことで、セッション内部で例外と完了を処理しながら、外側のメソッドからコントローラーへ簡潔な `IAsyncEnumerable<string>` を公開できます。

## 利用可能なモデルの一覧取得

`CopilotChatService.ListModelsAsync` は `CopilotClient.ListModelsAsync()` を呼び出し、接続中の Copilot CLI が実際に提供するモデルの ID と表示名を返します。

```csharp
var models = await _client.ListModelsAsync(cancellationToken);
```

モデル ID のハードコーディングは避けるべきです。利用可能なモデルはアカウント、ロールアウト、プロバイダーによって変わります。このデモでも以前、ハードコードされた一覧が古くなり、6モデルのうち1つしか動作しない状態になりました。API には引き続き
[`ChatController.AvailableModels`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/ChatController.cs)
に静的カタログがありますが、メタデータとフォールバックにのみ使用します。通常の経路では、SDK から現在のモデル一覧を取得します。

## 関連情報

- [SSE による応答のストリーミング](./02-sse-streaming.md)
- [小売ドメイン](./03-retail-analytics.md)
- [Blazor フロントエンド](./04-blazor-ui.md)
- ソース:
  [`CopilotChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs),
  [`Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs),
  [`ChatController.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/ChatController.cs)
