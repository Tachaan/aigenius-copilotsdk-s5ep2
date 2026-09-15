# ラボ 03 — ツール

**目標:** `CopilotTool.DefineTool` と `SessionConfig.Tools` を使用し、静的なプロンプトの
コンテキストを、モデルがオンデマンドで呼び出せる実際の C# 関数に置き換えます。

**所要時間:** 約20分

**前提条件:** [ラボ 02](../02-first-chat/)を完了していること。

## 手順 1 — ツールを使う理由

ラボ 02 では、小売に関する事実をシステムメッセージに含めることで、アシスタントに根拠を与えました。
小さな例では機能しますが、次の3つの問題があります。

1. コンテキストが静的であり、事前に貼り付けた内容しか認識できない
2. どの事実が重要かをモデルが推測する必要がある
3. 回答に不要な場合でも、すべての事実がトークンを消費する

ツールを使うと、問題の構造が変わります。プロンプトに適切なデータが含まれていることを期待する代わりに、
C# 関数を登録します。モデルは関数が必要なタイミングを判断し、SDK に呼び出しを要求して結果を受け取り、
最終回答を作成します。

## 手順 2 — ツールの形式を確認する

[`ToolsSample.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/ToolsSample.cs)
を開き、`GetCustomerTotal` を探します。

Copilot SDK のツールは、通常の C# メソッドから始まります。

```csharp
[Description("Gets the total amount a given retail customer has spent.")]
private static string GetCustomerTotal(
    [Description("Customer identifier, for example C003")] string customerId)
{
    ...
}
```

重要なのは、`System.ComponentModel` の `[Description]` メタデータです。

これらの説明はモデルにとっての API ドキュメントです。メソッドの説明が曖昧だと、モデルがツールを
選択しない可能性があります。パラメーターの説明が曖昧だと、誤った値を渡す可能性があります。
別の開発者向けにパブリック API を文書化するときと同じように、説明を記述してください。

## 手順 3 — ツールを登録する

`CopilotTool.DefineTool(GetCustomerTotal)` はメソッドを `AIFunction` に変換します。
次に、その関数をセッション構成に割り当てます。

```csharp
var modelId = await ModelPicker.PickAsync(client, requestedModelId);
var totalTool = CopilotTool.DefineTool(GetCustomerTotal);

var config = new SessionConfig
{
    Model = modelId,
    Streaming = false,
    Tools = [totalTool]
};
```

`Tools = [totalTool]` の行によって、「モデルにテキストのコンテキストがある」状態から、
「モデルがホストアプリケーションに実際の処理を要求できる」状態になります。
`ModelPicker` はこれらのラボで `claude-haiku-4.5` を優先モデルとして使用しますが、
利用できない場合はアカウントで使用可能なモデルにフォールバックします。`--model <id>` で上書きできます。

## 手順 4 — 実行する

```bash
dotnet run --project src/AgentOrchestrator/samples/SdkLabs -- tools
```

想定される出力:

```
== Lab 03: tools ==

Model: claude-haiku-4.5
Prompt: How much has customer C003 spent in total?


Assistant: 
  [tool] GetCustomerTotal(C003) -> $1,700.00

Assistant: Customer C003 has spent a total of **$1,700.00** across 2 transactions.
```

⚠️ 最初の空の `Assistant:` 行に注目してください。これは実際の動作です。最終的な自然言語の回答が
作成される前、ツール呼び出しの前後でアシスタントメッセージイベントが発生します。

## 手順 5 — 処理を追跡する

この実行には、次の4つの処理があります。

1. プロンプトが顧客 `C003` の合計支出額を尋ねる
2. モデルが、登録済みツールを使うことが適切な回答方法だと判断する
3. SDK が C# メソッドを呼び出し、`[tool]` 行を生成する
4. ツールの結果がモデルへ返され、モデルが最終回答を作成する

`[tool] GetCustomerTotal(C003) -> $1,700.00` 行は模擬出力ではありません。
SDK がモデルのツール呼び出しを処理している間に、実際の `GetCustomerTotal` メソッドが出力しています。

## 手順 6 — 実験する

`C999` など、存在しない顧客を試します。ツールは例外をスローせず、通常の文字列を返して処理します。

```csharp
Prompt = "How much has customer C999 spent in total? Use the available tool."
```

サンプルを再実行し、トランザクションが見つからなかったことをアシスタントが報告するか確認します。

次に、小売データを必要としないプロンプトを試します。

```csharp
Prompt = "In one short sentence, define average order value."
```

モデルは直接回答するはずです。顧客の検索が不要なため、`[tool]` 行は表示されません。

## 手順 7 — アクセス許可でツール実行を制御する

SDK は、プロセス内のアクセス許可フックも公開しています。

```csharp
OnPermissionRequest = (request, invocation) =>
{
    return Task.FromResult(PermissionDecision.ApproveOnce());
}
```

シグネチャは次のとおりです。

```csharp
Func<PermissionRequest, PermissionInvocation, Task<PermissionDecision>>
```

判定には `GitHub.Copilot.Rpc.PermissionDecision` の `ApproveOnce()` や
`Reject(string feedback)` などを使用します。すべての要求を許可するサンプル向けに、組み込みの
ショートカット `PermissionHandler.ApproveAll` も用意されています。

⚠️ GitHub Copilot SDK v1.0.9 では、このアクセス許可判定 API は試験的機能としてマークされています。
`GitHub.Copilot.Rpc.PermissionDecision` を使用すると、抑制しない限りビルドエラー `GHCP001` が
発生します。サンプルプロジェクトでは、次のファイルで意図的に抑制しています。
[`SdkLabs.csproj`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/SdkLabs.csproj):

```xml
<NoWarn>$(NoWarn);GHCP001</NoWarn>
```

⚠️ このフックを強制ポイントとして利用する場合は、細心の注意を払ってください。検証時には、
ホスト CLI がツールを事前承認していたため、ハンドラーは**一度も呼び出されませんでした**。
すべての要求を拒否するハンドラーでもコマンドは実行されました。`OnPermissionRequest` は、
ホストが判断を委ねた場合にのみ動作するフックとして扱ってください。制御に利用する前に、
**自分の**環境で実際に発火することを確認してください。

参考コードについては、
[`PermissionsSample.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/samples/SdkLabs/PermissionsSample.cs)
を参照してください。シェルフックを使った別のガバナンス手法については、
[追加 — ガバナンスフック](../extra-governance-hooks/)を参照してください。

ホストにとって適切な場合にツールをアクセス許可フローから除外するため、
`CopilotToolOptions.SkipPermission` も用意されています。

## ✅ チェックポイント

ここまでで、次の項目を説明できるようになりました。

- [x] 動的データをシステムメッセージに詰め込むより、ツールが適している理由
- [x] `[Description]` 属性がツールの選択と引数を導く仕組み
- [x] `CopilotTool.DefineTool` が C# メソッドを `AIFunction` として登録する仕組み
- [x] `SessionConfig.Tools` が関数をモデルから利用可能にする仕組み
- [x] 実際に実行するホストでアクセス許可フックを検証する必要がある理由

## 💡 発展課題

顧客が購入した製品カテゴリを返す2つ目のツールを追加します。たとえば、`C003` に対して
`Electronics` と `Fashion` を返します。メソッドとそのパラメーターに正確な `[Description]` 属性を付け、
`GetCustomerTotal` と並べて登録してから、次のように質問します。

```text
Which categories has customer C003 bought from, and how much have they spent?
```

モデルが片方のツール、両方のツールのどちらを呼び出すか、または直接回答するかを確認します。

## 関連資料

- 前へ: [ラボ 02 — 最初のストリーミングチャット](../02-first-chat/)
- 次へ: [ラボ 04 — イベント](../04-events/)
- [デモ: Copilot SDK の統合](../../demos/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
