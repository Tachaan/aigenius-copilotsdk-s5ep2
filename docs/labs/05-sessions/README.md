# ラボ 05 — セッション

**目標:** 「どこからでも使える自分のエージェント」の基盤となる、Copilot SDK の会話の
永続化と再開を実装します。

**所要時間:** 約 20 分

**前提条件:** [ラボ 04](../04-events/) を完了していること。

## 手順 1 — 永続化が重要な理由を理解する

セッションを永続化しない場合、プロセスを再起動するたびに記憶が失われます。アシスタントが
参照できるのは現在のプロセスで送信されたメッセージだけなので、CLI のクラッシュ、ブラウザーの
更新、サーバーの再起動によって会話が失われます。

セッションを保存すると、会話に識別子が与えられます。CLI で会話を開始し、Web アプリから
再開して、後からスマートフォンで続きを行えます。これが「どこからでも使える自分の
エージェント」の中核パターンです。クライアントが変わっても、セッション履歴は同じ ID に
関連付けられたままです。

このサンプルでは、まず限定的な動作を確認します。同じプロセス、同じ `CopilotClient` で
セッションを破棄した後に再開します。また `--resume <id>` もサポートしているため、同じ
セッション永続化ストアへアクセスでき、互換性のあるランタイムと適切な認可を利用できる環境では、
別の第 2 プロセスでも試せます。

## 手順 2 — 既知の ID でセッションを作成する

次のファイルを開き、
[`SessionsSample.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/SessionsSample.cs)
でセッション ID を確認します。

```csharp
var sessionId = $"sdklabs-{Guid.NewGuid():N}"[..24];
```

次に、それが SDK に渡されている箇所を確認します。

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    SessionId = sessionId,
    Model = modelId,
    Streaming = false
});
```

`SessionConfig.SessionId` を使うと、独自の id を指定できます。省略した場合は SDK が id を
生成しますが、後でセッションを再開するには、アプリでその生成値を取得して保存しておく
必要があります。

実際のアプリでは、会話 id やサポート案件 id など、ドメイン内で意味があり一意になる id を
使用してください。id にシークレットを含めないでください。id はログ、診断情報、URL に
表示されることがよくあります。

## 手順 3 — サンプルを実行する

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- sessions
```

想定される出力:

```
== Lab 05: sessions ==

Model: claude-haiku-4.5
Session id: sdklabs-7946e93975844b2e

--- Turn 1 (new session) ---
You: Remember this: my favourite retail segment is 'At Risk'. Reply with just OK.
Assistant: OK.

Session disposed.

--- Turn 2 (resumed session) ---
You: Which retail segment did I say was my favourite?
Assistant: 'At Risk'.

--- Session metadata ---
  id=sdklabs-7946e93975844b2e metadata retrieved
```

セッション ID は実行ごとにランダムに生成されるため、実際の値は異なります。重要なのは ID の
値そのものではなく、最初のセッションを破棄した後も同じ ID で再開したターン 2 が `'At Risk'` を記憶していた
ことです。

この実行で確認できるのは、1 つのプロセス内で破棄後に再開できることです。これだけでは、
デバイス間の引き継ぎや再起動後の復旧までは確認できません。

## 手順 4 — セッションを再開する

2 回目のターンでは同じ ID を使用しますが、別の SDK 呼び出しを使用します。

```csharp
await using var resumed = await client.ResumeSessionAsync(
    sessionId,
    new ResumeSessionConfig
    {
        Model = modelId,
        Streaming = false
    });
```

⚠️ **config パラメーターは必須です。** SDK v1.0.9 では、次のコードはコンパイルできません。

```csharp
await client.ResumeSessionAsync(sessionId);
```

必須の構成パラメーターに対応する引数がないため、コンパイラは `CS7036` を報告します。

⚠️ **`SessionConfig` ではなく `ResumeSessionConfig` を使用してください。** 新しいセッションの
作成には `SessionConfig`、既存のセッションの再開には `ResumeSessionConfig` を使用します。
再開用の構成には、ここで使用している `Model` や `Streaming` など同種の設定が含まれますが、
型は異なります。

さらに確実に確認するため、最初の実行で表示されたセッション ID を使用して、第 2 プロセスで
再開処理を実行します。

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- sessions --resume sdklabs-7946e93975844b2e
```

2 回目の起動で確認済みの出力:

```
== Lab 05: sessions ==

Model: claude-haiku-4.5
Session id: sdklabs-7946e93975844b2e

--- Resumed existing session ---
You: Which retail segment did I say was my favourite?
Assistant: 'At Risk'.

--- Session metadata ---
  id=sdklabs-7946e93975844b2e metadata retrieved
```

この 2 つ目のコマンドは、実際にプロセス境界を越えます。別のマシンから再開するには、さらに
同じセッション永続化ストアへアクセスでき、互換性のあるランタイムを実行し、保存済みセッションに
対する適切な認可を受けている必要があります。

## 手順 5 — 保存済みセッションを検出する

このサンプルでは、SDK にメタデータも要求します。

```csharp
var metadata = await client.GetSessionMetadataAsync(sessionId);
```

この呼び出しは、保存済みセッションのメタデータを返します。既知の ID から開始するのではなく、
利用可能な保存済みセッションを参照するには、`ListSessionsAsync(...)` を使用します。

```csharp
var sessions = await client.ListSessionsAsync(...);
```

一般的なパターンは次のとおりです。

1. サインインしているユーザーのセッションを一覧表示する
2. ユーザーに 1 つ選択してもらうか、最新のものを選択する
3. その ID を `ResumeSessionAsync(id, config)` に渡す

## 手順 6 — アーキテクチャに結び付ける

セッションの永続化により、次のことが可能になります。

- **デバイスやクライアント間の引き継ぎ** — ある場所で開始し、別の場所で続行する
- **クラッシュからの復旧** — コンテキストを最初から再構築せず、プロセスの再起動後に再開する
- **監査性** — 安定した ID により、会話の調査、整理、追跡が容易になる

現在のデモアプリでは、ブラウザーが `StorageService` を介してチャット履歴を localStorage に
保持します。これは 1 台のデバイス上の 1 つのブラウザーでは機能しますが、会話を別のデバイスへ
移動できません。スマートフォンや別のマシンでアプリを開くと、履歴はありません。

SDK セッションでこの問題を解決できます。UI は会話全体の代わりにセッション ID を保存でき、
同じセッションストアを使用する認可済みクライアントが、同じサーバー側セッションを再開できます。

⚠️ **セッション ID はアクセス制御ではありません。** ID は識別子として扱い、シークレットや
権限として扱わないでください。保存済みの会話を再開する前に、アプリでは通常どおりユーザーの
認証と認可が必要です。

## ⚠️ 注意点

- **ID の衝突:** セッション ID は保存済み会話を参照するキーです。ID を再利用すると、新しい会話を作成する代わりに
  古い会話が再開されます。
- **不透明な ID:** ランダムな ID はデモでは機能しますが、実際のシステムでは ID をユーザー、
  案件、ワークフローに対応付けられる必要があります。
- **ID は権限ではない:** ID を知っている、または推測できるだけで会話にアクセスできては
  いけません。認可は別途適用してください。
- **ID 内のシークレット:** セッション ID にトークン、メールアドレス、顧客のシークレット、
  機密データを含めないでください。
- **誤った再開オーバーロード:** `ResumeSessionAsync(sessionId)` は `CS7036` で失敗します。
  `ResumeSessionConfig` を渡してください。
- **誤った構成型:** `SessionConfig` は作成用、`ResumeSessionConfig` は再開用です。

## 💡 発展課題

同じセッションを 2 回再開します。

1. メタデータ呼び出しの後に 3 回目のターンを追加する
2. 同じ `sessionId` をもう一度再開する
3. 元の `'At Risk'` メッセージについて別の質問をする

または、保存済みセッションを一覧表示し、最新のセッションを再開します。

```csharp
var sessions = await client.ListSessionsAsync(...);
```

次に、選択した id を以下に渡します。

```csharp
await client.ResumeSessionAsync(id, new ResumeSessionConfig
{
    Model = modelId,
    Streaming = false
});
```

## ✅ チェックポイント

これで、次の項目を説明できるようになりました。

- [x] 永続化しない場合、プロセスの再起動でコンテキストが失われる理由
- [x] `SessionConfig.SessionId` により、アプリに安定した会話キーを与える方法
- [x] `ResumeSessionAsync(id, config)` に `ResumeSessionConfig` が必要な理由
- [x] `GetSessionMetadataAsync` と `ListSessionsAsync(...)` が保存済みセッションの検出に
  役立つ仕組み
- [x] SDK セッションがデバイス間のチャット履歴に適した基盤である理由
- [x] プロセス間およびデバイス間の再開が、共有ストレージ、互換性のあるランタイム動作、
  認可にも依存する理由

## 関連項目

- 前へ: [ラボ 04 — イベント](../04-events/)
- 次へ: [ラボ 06 — MCP](../06-mcp/)
- [デモ: Copilot SDK の統合](../../demos/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
