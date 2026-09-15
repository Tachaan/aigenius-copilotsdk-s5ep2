# SSE による応答のストリーミング

このウォークスルーでは、ASP.NET Core API から Blazor WebAssembly ブラウザークライアントまで、チャット応答の流れを追います。SSE の正確なワイヤ形式、フラッシュが重要な理由、クライアントがストリーミングされたチャンクを解析する方法を説明します。

## API エントリーポイント

[`ChatController.StreamChat`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/ChatController.cs)
は `POST /api/chat/stream` を処理します。`ChatRequest` を受け取り、指定されたモデルまたは既定の `claude-haiku-4.5` を選択し、応答を Server-Sent Events として構成します。

```csharp
Response.ContentType = "text/event-stream";
Response.Headers.CacheControl = "no-cache";
Response.Headers.Connection = "keep-alive";
```

これらのヘッダーは、中継コンポーネントとブラウザーに対して、これが完了までバッファリングすべき通常の JSON 応答ではなく、長時間維持されるストリームであることを示します。

## ワイヤ形式

[`CopilotChatService.ChatStreamAsync`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs)
からチャンクを受け取るたびに、コントローラーは小さな JSON オブジェクトをシリアライズし、SSE メッセージを1件書き込みます。

```text
data: {"content":"..."}

```

ストリームが正常に完了すると、エンドポイントはセンチネルを書き込みます。

```text
data: [DONE]

```

ストリームの開始後に例外が発生した場合、コントローラーは HTTP エラー応答へ切り替えるのではなく、同じ SSE ストリーム内にエラーイベントを書き込みます。

```text
data: {"error":"..."}

```

その時点では、HTTP エラーステータスへ確実に切り替えることはできません。ステータスコードと応答ヘッダーはすでに送信済みなので、後から発生した障害を通知する実用的な方法は、ストリームのペイロードに含めることだけです。

## 各チャンクのフラッシュ

`ChatController.StreamChat` は、コンテンツチャンクを書き込むたびに本文をフラッシュします。

```csharp
await Response.WriteAsync($"data: {data}\n\n", cancellationToken);
await Response.Body.FlushAsync(cancellationToken);
```

`FlushAsync` がないと、サーバー、ホスト、プロキシ、ブラウザーのいずれかがデータをバッファリングする可能性があります。SDK が差分を正しく生成していても、バッファーが一杯になるかリクエストが終了するまでユーザーには何も表示されず、ストリーミングが壊れているように見えます。

## キャンセル

`StreamChat` は、ASP.NET Core が提供するリクエストの `CancellationToken` を受け取ります。コントローラーはそれを `CopilotChatService.ChatStreamAsync` に渡し、ループ中に `IsCancellationRequested` を確認し、さらに `WriteAsync` と `FlushAsync` にも渡します。ブラウザータブが閉じられた場合やリクエストが破棄された場合、API は書き込みを停止してストリーミング処理を終了できます。

## ブラウザークライアント

Blazor クライアントのコードは
[`ChatService.StreamChatAsync`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/ChatService.cs)
にあります。`HttpCompletionOption.ResponseHeadersRead` を指定して `/api/chat/stream` に POST します。

```csharp
using var response = await _http.SendAsync(
    httpRequest,
    HttpCompletionOption.ResponseHeadersRead);
```

`ResponseHeadersRead` は、応答ヘッダーが到着した時点ですぐに制御を返すため重要です。これによりクライアントは、応答全体を待たずに本文ストリームを1行ずつ読み取れます。

パーサーは空行を無視し、`data: ` プレフィックスを探し、`[DONE]` で停止して JSON データイベントを解析します。`content` の値は UI に返され、`error` の値は例外になります。

## 小売分析用のシステムプロンプト

呼び出し元がシステムメッセージを指定しない場合、`ChatService.StreamChatAsync` は既定のシステムメッセージを送信します。このプロンプトは、アシスタントを食料品小売業者向けの小売分析アシスタントとして位置付け、デモのコンテキストを提供し、Markdown の表や箇条書きを使ったデータ主導のビジネスインサイトを求めます。また、コードを変更したり、コード変更を提案したりしないよう指示します。

[`Home.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Pages/Home.razor)
は、ユーザーのプロンプトと選択したモデルを `ChatService.StreamChatAsync` に渡します。そのため、リクエストが API に到達する前に、クライアントサービスによって既定のシステムプロンプトが適用されます。

## curl で試す

ローカル API が使用しているポートにリクエストを送信します。たとえば、API が Web クライアントの既定の API ベースアドレスで待ち受けている場合は、curl が応答をバッファリングしないよう `curl -N` を使ってストリーミングリクエストを送信します。

```bash
curl -N -X POST http://localhost:5050/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarise customer C003 and recommend a segment.",
    "model": "claude-haiku-4.5",
    "systemMessage": "You are a retail analytics assistant."
  }'
```

複数の `data: {"content":"..."}` メッセージが表示され、その後に `data: [DONE]` が続きます。

## 関連情報

- [Copilot SDK の組み込み](./01-copilot-sdk-integration.md)
- [小売ドメイン](./03-retail-analytics.md)
- [Blazor フロントエンド](./04-blazor-ui.md)
- ソース:
  [`ChatController.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/ChatController.cs),
  [`CopilotChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs),
  [`ChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/ChatService.cs),
  [`Home.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Pages/Home.razor)
