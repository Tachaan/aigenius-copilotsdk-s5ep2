# ラボ 02 — 最初のストリーミングチャット

**目標:** 1つのプロンプトが、ブラウザー → API → Copilot SDK → モデル → ブラウザーという
スタック全体を通る流れを追跡し、モデル一覧をハードコードせず実行時に取得する理由を理解します。

**所要時間:** 約20分

**前提条件:** [ラボ 01](../01-setup/)を完了し、両方のサービスが実行中であること。

## 手順 1 — ワイヤーフォーマットを確認する

プロンプトを送信し、生の Server-Sent Events を確認します。

```bash
curl -N -X POST http://localhost:5050/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Name three retail KPIs. One line each.","model":"claude-haiku-4.5"}'
```

1つの大きな応答ではなく、多数の小さなフレームが表示されます。

```
data: {"content":"1. **Average"}

data: {"content":" Transaction Value** — revenue divided by"}

data: {"content":" transaction count.\n"}

...

data: [DONE]
```

次の3点に注目してください。

1. 各フレームは `data: `、JSON、**空行**の順で構成されます。この空行を SSE がイベントの区切りとして使用します
2. チャンクは単語や文の途中を含む任意の位置で分割されます。クライアントはチャンクを連結する必要があり、完全なトークンが届くとは想定できません
3. ストリームは番兵値 `data: [DONE]` で終了します

## 手順 2 — サーバー側を確認する

[`ChatController.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Controllers/ChatController.cs)
を開き、`StreamChat` を探します。次の点を順番に確認してください。

- `Response.ContentType = "text/event-stream"` と、`no-cache` および keep-alive
- `_chatService.ChatStreamAsync(...)` を処理する `await foreach`
- **すべての**チャンクの後にある `await Response.Body.FlushAsync(cancellationToken)`
- 末尾の `data: [DONE]`

⚠️ **フラッシュは省略できません。** フラッシュしないと ASP.NET Core が応答をバッファリングし、
クライアントはすべてを一度に受信します。ストリーム自体は「動作」していても、入力中のように見える効果は
完全に失われます。これは SSE エンドポイントを構築するときに最もよくある間違いです。

次に `catch` ブロックを確認します。ストリーム開始後のエラーは HTTP 500 として返されるのではなく、
`data: {"error":"..."}` として**同じ SSE ストリーム内**に返されます。これは必須の動作です。
最初のチャンクとともにステータス行とヘッダーがすでに送信されているため、後からステータスコードを変更できません。

## 手順 3 — SDK 統合を確認する

[`CopilotChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs) を開きます。

`ChatStreamAsync` はセッションを作成し、イベントを購読します。

```csharp
session.On<SessionEvent>(evt =>
{
    switch (evt)
    {
        case AssistantMessageDeltaEvent delta:
            outputChannel.Writer.TryWrite(delta.Data.DeltaContent ?? "");
            break;
        case SessionIdleEvent:
            done.SetResult();
            break;
        ...
    }
});
```

⚠️ **明示的な `<SessionEvent>` が重要です。** SDK v1.x では、ラムダ式から型引数が
推論されなくなりました。`session.On(evt => ...)` は `CS0411` でコンパイルに失敗します。
v0.x 向けに書かれた古いサンプルでは、今も非ジェネリック形式が使われています。

`Channel<string>` にも注目してください。SDK セッションはバックグラウンドの `Task` 内で実行され、
完成したチャンクは列挙子が読み取るチャネルへプッシュされます。この間接化が必要なのは、C# では
`try`/`catch` 内の `yield return` が禁止されており、セッション処理には実際に例外処理が必要だからです。

## 手順 4 — 利用可能なモデルを API に問い合わせる

```bash
curl -s http://localhost:5050/api/chat/models | jq -r '.[].id'
```

一覧は**自分のアカウント**からリアルタイムに取得されます。次に、一覧にはほぼ確実に存在しないモデルを試します。

```bash
curl -N -X POST http://localhost:5050/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello","model":"gpt-4-turbo-preview"}'
```

想定される出力:

```
data: {"error":"... Model \"gpt-4-turbo-preview\" is not available."}
```

これが、`ChatController.GetModels` が固定リストを返さず、
`CopilotChatService.ListModelsAsync()` を呼び出す理由です。このデモの以前のバージョンでは、
6つのモデル ID がハードコードされていましたが、時間の経過とともに5つが無効になり、モデル選択欄には
使用時に失敗するモデルが表示され続けていました。現在、静的カタログは CLI に接続できない場合の
フォールバックとしてのみ存在します。

## 手順 5 — モデルを切り替えて比較する

ライブリストから2つの ID を選び、同じ質問をします。

```bash
MODEL=$(curl -s http://localhost:5050/api/chat/models | jq -r '.[0].id')
echo "Using $MODEL"

curl -N -X POST http://localhost:5050/api/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"In one sentence, what is customer churn?\",\"model\":\"$MODEL\"}"
```

別の ID でも繰り返し、待ち時間と応答の調子を比較します。ブラウザーの **Model** ドロップダウンも
同じ処理を行い、選択内容は `StorageService` によって localStorage に保存されます。

💡 ブラウザーに保存されたモデルが後でアカウントから利用できなくなった場合、`Home.razor` は
読み込み時に古い値を検出します。最初の送信時に失敗するのではなく、有効なモデルへフォールバックします。

## 手順 6 — システムメッセージで応答を調整する

API はオプションの `systemMessage` を受け取ります。組み込みの指示を置き換えず補足するように、
**append** モードで適用されます。

```bash
curl -N -X POST http://localhost:5050/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt":"Which segment has the lowest retention?",
    "model":"claude-haiku-4.5",
    "systemMessage":"You are a retail analytics assistant. Context: 4 segments — High Value (92% retention), Regular (78%), At Risk (45%), New (65%). Answer in one sentence."
  }'
```

想定されるのは、45% の **At Risk** を挙げる、根拠に基づいた回答です。

このコンテキストがなければ、モデルはシードデータにアクセスできず、その旨を回答します。
`systemMessage` を削除して再実行し、比較してください。Blazor クライアントは常に小売分析用の
システムメッセージを送信するため、UI はドメインを理解しているように動作します。
`ChatService.StreamChatAsync` を参照してください。

このラボでは、**システムメッセージ**を通じてコンテキストを渡しました。これは静的であり、呼び出すたびに
トークンを消費します。ラボ 03 では、実際に小売データが必要なときにモデルがオンデマンドで呼び出せる
**ツール**に置き換えます。

## ✅ チェックポイント

ここまでで、次の項目を説明できるようになりました。

- [x] SSE のワイヤーフォーマットと、各チャンクをフラッシュする理由
- [x] エラーを HTTP ステータスコードで返さず、ストリーミングする理由
- [x] `On<SessionEvent>` に明示的な型引数が必要な理由
- [x] 実行時にモデルを検出する理由
- [x] システムメッセージによってアシスタントに小売ドメインの根拠を与える方法

## 関連資料

- 次へ: [ラボ 03 — ツール](../03-tools/)
- [デモ: Copilot SDK の統合](../../demos/01-copilot-sdk-integration.md)
- [デモ: SSE ストリーミング](../../demos/02-sse-streaming.md)
