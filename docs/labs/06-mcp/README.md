# ラボ 06 — Model Context Protocol (MCP)

**目標:** Model Context Protocol サーバーを Copilot SDK セッションに接続し、自分で作成して
いないツールをエージェントが利用できるようにします。

**所要時間:** 約 20 分

**前提条件:** [ラボ 05](../05-sessions/) を完了していること、および HTTP MCP サーバーに
アクセスするためのインターネット接続。

## 手順 1 — MCP によって追加されるものを理解する

[ラボ 03](../03-tools/) では、C# 関数を作成して自分で登録することで、モデルにツールを
提供しました。これは強力ですが、すべての機能が依然として自分で所有、テスト、保守する
コードです。

MCP は問題の構造を変えます。Model Context Protocol サーバーは標準プロトコルを介して
ツールセット全体を公開し、SDK はそのサーバーをセッションに接続できます。モデルは通常の
推論ループの一部として、そのサーバーのツールを検出して呼び出します。

このラボで使用する外部ツールセットは Microsoft Learn です。`SearchDocsAsync` 関数を
作成する代わりに、Learn MCP サーバーへ接続し、エージェントが製品ドキュメントを直接
参照できるようにします。

## 手順 2 — MCP トランスポートを選択する

SDK には 2 種類の MCP サーバー構成型があります。

```csharp
McpServers = new Dictionary<string, McpServerConfig>
{
    ["microsoft.docs.mcp"] = new McpHttpServerConfig
    {
        Url = "https://learn.microsoft.com/api/mcp"
    }
};
```

サーバーがすでにどこかで稼働しており、HTTP 経由で到達できる場合は
`McpHttpServerConfig` を使用します。今回はこれに該当します。Microsoft Learn が
`https://learn.microsoft.com/api/mcp` でサーバーをホストしているため、ローカルに
インストールするものはありません。

SDK からローカル MCP プロセスを起動し、標準入出力で通信する場合は
`McpStdioServerConfig` を使用します。この形式は、ローカルファイルシステムツール、
データベースヘルパー、マシン上でコマンドラインプログラムとして動作する言語固有の
MCP サーバーでよく使用されます。

モデルから見れば、どちらのトランスポートでも結果は同じです。名前付き MCP ツールが
セッション内で利用可能になります。

## 手順 3 — サンプルを構成して実行する

次のファイルを開き、
[`McpSample.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/McpSample.cs)
で `SessionConfig` を確認します。

```csharp
var modelId = await ModelPicker.PickAsync(client, requestedModelId);

var config = new SessionConfig
{
    Model = modelId,
    Streaming = false,
    McpServers = new Dictionary<string, McpServerConfig>
    {
        ["microsoft.docs.mcp"] = new McpHttpServerConfig
        {
            Url = "https://learn.microsoft.com/api/mcp"
        }
    },
    OnPermissionRequest = PermissionHandler.ApproveAll
};
```

`SessionConfig.McpServers` プロパティの型は `IDictionary<string, McpServerConfig>` です。
キーはサーバー名、値はトランスポート固有のサーバー構成オブジェクトです。

このサンプルでは `OnPermissionRequest = PermissionHandler.ApproveAll` も設定します。検証時は
ホスト CLI が MCP ツールの使用を事前承認していたようで、このハンドラーの呼び出しは確認
できませんでした。この行が常に必須である証拠ではなく、念のための追加策として扱ってください。
権限に関する注意事項は [ラボ 03](../03-tools/) で扱った内容と同様です。

サンプルを実行します。

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- mcp
```

検証済みの実行で想定される出力:

```
== Lab 06: mcp ==

Model: claude-haiku-4.5
Prompt: asking the model to consult Microsoft Learn docs

  [mcp] SessionMcpServersLoadedEvent

Assistant: I don't have dedicated "Microsoft Learn tools" in my available toolset.
However, I can use the `web_fetch` tool to retrieve current information.
  [tool] ToolExecutionStartEvent: web_fetch
  [tool] ToolExecutionCompleteEvent: web_fetch (success=True)

Assistant: Based on Microsoft Learn documentation: **Azure Container Apps is a
serverless platform for running containerized applications without managing the
underlying infrastructure.** It supports API endpoints, background jobs,
event-driven processing and microservices, scaling automatically.

⚠️  No MCP tool was invoked.
    The model used non-MCP tool(s) instead: web_fetch
    The answer may have come from the model's own knowledge or a built-in
    tool rather than Microsoft Learn. Check the server is reachable and that
    its tools were loaded — look for the [mcp] lines above.
```

⚠️ **この出力を注意深く確認してください。ここがこのラボの要点です。**

回答は信頼できそうに見え、Microsoft Learn まで引用しています。しかし、これは
MCP の結果では**ありません**。`SessionMcpServersLoadedEvent` が発生したためサーバー構成は
受け入れられていますが、サーバーのツールはモデルに提供されていません。そのためモデルは
組み込みの `web_fetch` にフォールバックし、それでももっともらしい回答を生成しました。

最後のチェックがなければ、誤設定されたまま気付かれず、MCP デモが成功したという誤った安心感を
持っていたでしょう。このサンプルはまさにその誤判定を防ぐためにあり、そのためここでは終了コードが
**0 以外**になります。

> **この環境での状態:** Learn MCP サーバーは読み込まれますが、セッションにツールが公開
> されません。解決するまでは、上記の ⚠️ の経路を想定される出力として扱ってください。
> MCP ツールが実際に読み込まれた場合、最終行には
> `✅ MCP tool(s) invoked: <server>/<tool>` と表示され、終了コードは 0 になります。

## 手順 4 — MCP ツールが使用されたことを確認する

サンプルは SDK イベントを購読し、重要なイベントをログに記録します。

- `SessionMcpServersLoadedEvent` — サーバー構成が受け入れられた
- `McpToolsListChangedEvent` — サーバーがツール一覧を公開した
- `ToolExecutionStartEvent` / `ToolExecutionCompleteEvent` — ツールが実際に実行された

重要なのは、ツールを *MCP* と判定する方法です。`ToolExecutionStartEvent` には
`McpServerName` が含まれ、これが設定されている実行だけを数えます。`web_fetch` のような
組み込みツールにはサーバー名がないため、ログには記録されますが成功には数えられません。

```csharp
if (!string.IsNullOrWhiteSpace(start.Data.McpServerName))
{
    mcpTools.Add(toolName);
}
```

⚠️ このサンプルの以前のバージョンでは、*すべての*ツール実行を数え、MCP とは無関係な
ツールを成功として `✅ MCP tool(s) invoked: web_fetch` と報告していました。誤った対象を
数えることは、確認しないことよりも危険です。誤った安心感を生み出すためです。

MCP ツールが実行されなかった場合、サンプルは次を出力します。

```text
⚠️  No MCP tool was invoked.
    The model used non-MCP tool(s) instead: web_fetch
```

そして 0 以外で終了します。これにより、スクリプトがモデル単独のもっともらしい回答を、
MCP を利用した実行の成功と誤認することを防ぎます。Azure Container Apps は公開情報であり、
MCP ツールが利用できなくてもモデル自身の学習データから回答できるため、この区別が重要です。

## 手順 5 — エディターの MCP 構成と比較する

このリポジトリでは、VS Code 用に同じサーバーがすでに
次の [`.vscode/mcp.json`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.vscode/mcp.json)
で構成されています。

```json
{
  "servers": {
    "microsoft.docs.mcp": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

このファイルはエディター用です。`SessionConfig.McpServers` は、アプリまたはサンプル内で
実行される Copilot SDK セッション用です。利用側は異なりますが、同じプロトコルで同じ
サーバーと通信します。

これが MCP の要点です。1 つのプロトコルを多数のクライアントで利用できます。同じツール
サーバーを、エディター、CLI、テストハーネス、アプリケーションエージェントから利用できます。

## 手順 6 — MCP の利用と MCP の*提供*を比較する

ここまでは、セッションを外部のサーバーへ接続してきました。このリポジトリでは MCP サーバー
自体も**実装**しています。その理由を理解することが重要です。

これまで `CopilotChatService` は、アプリ自身のデータへアクセスできない状態でプロンプトを
モデルへ送信していました。チャットで「支出額が最も多い顧客は誰ですか」と尋ねても、モデルは
推測するしかありません。小売データベースがモデルから見えなかったためです。

[`AgentHQDemo.McpServer`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.McpServer/RetailTools.cs)
は、`retail.db` に対する 5 つの read-only ツールでこの隔たりを解消します。

| ツール | 回答できる質問 |
|:-----|:--------|
| `list_transactions` | 「C003 の最近の購入を表示して」 |
| `get_transaction` | 「トランザクション 7 の内容は？」 |
| `list_segments` | 「どのセグメントがありますか？」 |
| `get_customer_summary` | 「C001 の合計支出額は？」 |
| `predict_segment` | 「C003 はどのセグメントに属しますか？」 |

このサーバーは `ModelContextProtocol` パッケージ上に構築されたコンソールアプリで、
属性によって登録します。

```csharp
builder.Services
    .AddMcpServer(options => options.ServerInfo = new() { Name = "retail-analytics", Version = "1.0.0" })
    .WithStdioServerTransport()
    .WithToolsFromAssembly();
```

```csharp
[McpServerTool(Name = "get_customer_summary", ReadOnly = true, Destructive = false)]
[Description("Summarises one customer's spending: total, average, transaction count ...")]
public static async Task<CustomerSummaryDto> GetCustomerSummaryAsync(...)
```

⚠️ **stdio は stdout でプロトコルを伝送する**ため、すべてのログを stderr に出力する必要が
あります。意図しない `Console.WriteLine` があるとストリームが破損し、サーバーがハングした
ように見えます。

```csharp
builder.Logging.AddConsole(options =>
{
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});
```

[`CopilotChatService`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Services/CopilotChatService.cs)
は、手順 2 の `McpStdioServerConfig` 形式を使用してこのサーバーを接続します。

```csharp
McpServers = new Dictionary<string, McpServerConfig>
{
    ["retail-analytics"] = new McpStdioServerConfig
    {
        Command = "dotnet",
        Args = [serverDll],
        WorkingDirectory = apiDirectory
    }
};
```

ここで本当に学ぶべき設計判断は 2 つあります。

**1. コードだけでなく接続でも最小権限を適用する。** コンテキストは `Mode=ReadOnly` で
開かれるため、書き込みは SQLite 自体によって拒否されます。

```csharp
options.UseSqlite($"Data Source={dbPath};Mode=ReadOnly");
```

プロンプトに命令が紛れ込んでも、そもそも権限が付与されていないためデータを変更できません。
「単に `SaveChangesAsync` の呼び出しを書かなかった」という方法と比較してください。後者は
規約であって、制御ではありません。

**2. 生の SQL ではなくドメインツールを提供する。** モデルに渡すのは `run_query` ではなく
`get_customer_summary` です。汎用 SQLite MCP サーバーならコードを追加せずに済みますが、
モデルに任意の SQL を実行できる抜け道も与えてしまいます。ツールの公開面そのものが
セキュリティ境界であるため、小さく具体的に保ってください。

変更されて**いない**点にも注目してください。REST API は引き続き `RetailAnalyticsService` を
介してデータベースを直接読み取ります。MCP は*モデル*のためのものであり、アプリが自身の
データベースと通信するためのものではありません。自前の CRUD を LLM ツールプロトコル経由に
すると、利点がないままサブプロセスへの経由が増え、トランザクションと型安全性が失われます。

試してみましょう。

```bash
dotnet run --project src/AgentOrchestrator/AgentHQDemo.Api
```

```bash
curl -s -X POST http://localhost:5050/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is customer C003 total spend and which segment are they in?"}'
```

手順 4 と同様に、証拠となる API ログを確認します。

```
MCP tool call: retail-analytics/get_customer_summary
MCP tool call: retail-analytics/predict_segment
```

💡 **権限ハンドラーは一律ではなく、範囲を限定しています。** `PermissionHandler.ApproveAll` は
コンソールラボでは問題ありませんが、このサービスにはブラウザーから到達できるため、
`retail-analytics` の read-only ツールだけを承認します。

```csharp
if (request is PermissionRequestMcp mcp
    && mcp.ServerName == RetailMcpServer
    && mcp.ReadOnly)
{
    return Task.FromResult(PermissionDecision.ApproveOnce());
}
```

これは主要な制御ではなく、多層防御として扱ってください。
[権限診断](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/PermissionsSample.cs)
の記録どおり、ホスト CLI がツールの承認を事前付与している場合、フックの呼び出しは確認されて
いません。実際に制約を保証するのは `Mode=ReadOnly` 接続です。

## ⚠️ 注意点

- `McpServers` は `Dictionary<string, object>` ではありません。
  正しい型は `IDictionary<string, McpServerConfig>` であるため、値の型を変換できず、よくあるこの省略形は
  `CS0266` などのコンパイルエラーで失敗します。
- Learn サーバーにはネットワーク経由で接続します。到達できない場合、モデルに MCP ツールは
  なく、自身の知識から何事もなく回答する可能性があります。このサンプルは現在、
  `ToolExecutionStartEvent` を確認できない限り 0 以外で終了します。
- MCP サーバーはサードパーティのコードであり、強力な機能を公開する可能性があります。実務を
  扱うエージェントへ追加する前に、サーバー、権限、データアクセスを精査してください。
- stdio MCP サーバーは stdout に一切書き込んではいけません。すべてのログを stderr へ
  送らないと、プロトコルストリームが破損し、サーバーがハングしたように見えます。
- read-only の*ヒント*は read-only の*保証*ではありません。`ReadOnly = true` はホストに
  自動承認しても安全だと伝えますが、`AgentHQDemo.McpServer` で実際に書き込みを防ぐのは
  `Mode=ReadOnly` 接続文字列です。

## 💡 発展課題

基本の実行が成功したら、次のいずれかを試してください。

- 2 つ目の MCP サーバーを追加し、モデルがツールセットを選択する方法を比較する。
- サーバー名を `DisabledMcpServers` に追加して同じプロンプトを再実行し、Microsoft Learn
  ツールが利用できる場合とできない場合の回答を比較する。
- 認証が必要な MCP シナリオや、より高度な MCP シナリオが必要な場合に、
  `McpOAuthTokenStorage`、`GitHubMcpToolConfig`、`EnableMcpApps` などの関連 SDK 構成を調べる。

## ✅ チェックポイント

これで、次の項目を説明できるようになりました。

- [x] MCP と C# で直接作成するツールの違い
- [x] `McpHttpServerConfig` と `McpStdioServerConfig` を使い分ける場面
- [x] `SessionConfig.McpServers` が名前を使ってサーバーを接続する仕組み
- [x] もっともらしい回答だけでは MCP ツールが呼び出された証拠にならない理由
- [x] `.vscode/mcp.json` と SDK 構成で同じサーバーを対象にできる仕組み
- [x] このリポジトリが MCP サーバーを利用するだけでなく*提供*する理由、および REST API が
      引き続きデータベースと直接通信する理由
- [x] `Mode=ReadOnly` が実際の制御であり、`ReadOnly = true` はヒントにすぎない理由

## 関連項目

- 前へ: [ラボ 05 — セッション](../05-sessions/)
- 次へ: [ラボ 07 — まとめ](../07-wrap-up/)
- [デモ: Copilot SDK の統合](../../demos/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
