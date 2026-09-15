# ラボ 03 — ツール

**目的:** `@define_tool`、Pydantic のパラメーターメタデータ、
`client.create_session(..., tools=[...])` を使って、静的なプロンプト コンテキストを
モデルが必要に応じて呼び出せる実際の Python 関数に置き換えます。

**所要時間:** 約20分です。

**前提条件:** [ラボ 02](../02-first-chat/) を完了していること。

## ステップ 1 — ツールが必要な理由

ラボ 02 では、小売データの事実をシステムメッセージに送ることでアシスタントに文脈を与えました。
この方法は小さな例では機能しますが、問題が 3 つあります。

1. コンテキストが静的で、最初に貼り付けた内容しか認識できません。
2. どの事実が重要かをモデルが推測しなければなりません。
3. 答えに不要な場合でも、すべての事実がトークンを消費します。

ツールを使うと、問題の扱い方そのものが変わります。プロンプトに正しいデータが含まれていることを期待する代わりに、Python 関数を登録します。モデルはその関数が必要なタイミングを判断し、SDK に呼び出しを依頼し、結果を受け取ってから最終的な回答を書きます。

## ステップ 2 — ツールの形を確認する

[`sdk_labs/tools_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/tools_sample.py)
を開き、`get_customer_total` を探します。

Copilot SDK のツールは、Pydantic のパラメーターモデルを受け取る通常の Python 関数として始まります。

```python
class GetCustomerTotalParams(BaseModel):
    """Parameter schema sent to the model.

    Where C# reads ``[Description]`` attributes off the method signature, Python
    describes parameters with a Pydantic model — the field descriptions are what
    the model sees.
    """

    customer_id: Annotated[str, Field(description="Customer identifier, for example C003")]


@define_tool(description="Gets the total amount a given retail customer has spent.")
def get_customer_total(params: GetCustomerTotalParams, _invocation: ToolInvocation) -> str:
    matches = [t for t in TRANSACTIONS if t[0].casefold() == params.customer_id.casefold()]

    if not matches:
        return f"No transactions found for {params.customer_id}."

    total = sum(t[1] for t in matches)
    print(f"  [tool] get_customer_total({params.customer_id}) -> ${total:,.2f}")
    return f"{params.customer_id} has {len(matches)} transactions totalling ${total:,.2f}."
```

必要なシグネチャは
`(params: SomePydanticModel, _invocation: ToolInvocation) -> str` です。

C# との学習上の重要な違いはメタデータです。.NET ではメソッドとパラメーターに
`[Description]` 属性を使います。Python では次を使います。

- ツールの説明には `@define_tool(description=...)` を使います。
- パラメーターの説明には、Pydantic モデルのフィールドに `Field(description=...)` を使います。

これらの説明は、モデルにとっての API ドキュメントです。説明が曖昧だとツールが選ばれなかったり引数が誤ったりするため、公開 API のつもりで記述してください。

## ステップ 3 — ツールを登録する

このサンプルではクライアントを作成し、モデルを選択してから、セッション作成時にツールを登録します。

```python
async with CopilotClient() as client:
    model_id = await model_picker.pick(client, requested_model_id)
    if model_id is None:
        return 1

    session = await client.create_session(
        model=model_id,
        streaming=False,
        tools=[get_customer_total],
        # Required in Python, unlike .NET: the runtime asks permission before
        # invoking a custom tool, and with no handler the call is denied and
        # the model reports a permission error instead of an answer.
        on_permission_request=PermissionHandler.approve_all,
    )
```

この `tools=[get_customer_total]` という 1 行が、「モデルが多少のテキスト文脈を持っている」状態と、「モデルがホスト アプリケーションに実際の処理を依頼できる」状態の違いです。

`model_picker` は、これらのラボでは `claude-haiku-4.5` を優先モデルとして使いますが、アカウントで利用可能な具体的なモデルへフォールバックします。次のように指定すると上書きできます。

```bash
uv run python -m sdk_labs tools --model gpt-5
```

## ステップ 4 — 権限ハンドラーを省略しない

⚠️ これは .NET のサンプルと本当に異なる点です。

Python では、セッション作成時に `on_permission_request` を渡さない限り、カスタムツールの呼び出しは拒否されます。これがないと、モデルはツールの結果ではなく権限エラーを受け取り、エラーとして応答します。

すべてのリクエストを許可するラボ用サンプルでは、次を使います。

```python
on_permission_request=PermissionHandler.approve_all
```

本番コードでは、代わりにポリシー関数を実装してください。セキュリティ上の注意点はステップ 8 で扱います。

## ステップ 5 — 実行する

`src/AgentOrchestrator-python` から実行します。

```bash
uv run python -m sdk_labs tools
```

想定される出力は次のとおりです。

```text
== Lab 03: tools ==

Model: claude-haiku-4.5
Prompt: How much has customer C003 spent in total?

  [tool] get_customer_total(C003) -> $1,700.00

Assistant: Customer C003 has spent a total of **$1,700.00** across 2 transactions.
```

⚠️ **出力されていないもの**にも注目してください。.NET の実行記録と異なり、この Python サンプルには先頭の空の `Assistant:` 行がありません。最初のアシスタントイベントにはツール要求しか含まれないため、`tools_sample.py` では内容が空のアシスタントメッセージを意図的に無視しています。

## ステップ 6 — 何が起きたかを追う

この実行には、4 つの要素があります。

1. プロンプトが customer `C003` の合計支出を尋ねます。
2. モデルが、登録済みツールが答えに適していると判断します。
3. SDK が Python 関数を呼び出し、その結果として `[tool]` 行が出力されます。
4. ツール結果がモデルに返され、モデルが最終回答を書きます。

`[tool] get_customer_total(C003) -> $1,700.00` という行は模擬出力ではありません。SDK がモデルのツール呼び出しを処理している間に、実際の `get_customer_total` 関数が出力しています。

このツールが返すのは SDK 独自の結果オブジェクトではなく、通常の文字列です。

```python
return f"{params.customer_id} has {len(matches)} transactions totalling ${total:,.2f}."
```

## ステップ 7 — イベントの受け渡しを理解する

このサンプルでも、ラボ 02 で見たイベントモデルを使っています。Python のイベントはプッシュ専用のコールバックです。`session.on(handler)` がハンドラーを登録し、購読解除用の呼び出し可能オブジェクトを返します。非同期イテレーターはありません。

`SessionEvent` は `data`、`id`、`timestamp`、`type` などのフィールドを持つ 1 つのデータクラスです。`type` は `SessionEventType` 列挙型なので、Python では `evt.type` で分岐します。これは、イベントごとに 1 つのサブクラスを使う .NET のパターンと本質的に異なります。

[`sdk_labs/_common.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py)
にある共通の `IdleWaiter` は、セッションがアイドル状態に到達しない場合にサンプルが無限に待ち続けることを防ぎます。

## ステップ 8 — 権限によってツール実行を制御する

SDK は `on_permission_request` を通じて、プロセス内の権限フックを公開しています。カスタムポリシーはリクエストを調べ、`copilot.rpc` のいずれかの判定オブジェクトを返せます。たとえば次のように使います。

```python
from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject

# Not re-exported at the package root in SDK 1.0.9 — import it from the module.
from copilot.session import PermissionInvocation
```

参照用の診断コードは次を実装しています。

```python
def on_permission_request(
    request: PermissionRequest, invocation: PermissionInvocation
) -> PermissionRequestResult:
    # `kind` is a class attribute on each request type ("shell", "custom-tool",
    # "write", …), where the C# version reads a `Kind` property off one type.
    kind = getattr(request, "kind", "")
    tool_name = getattr(request, "tool_name", "") or ""
    print(f"  [permission] requested: kind={kind} tool={tool_name or '(n/a)'}")

    # Policy: allow reads, refuse anything destructive.
    if "delete" in f"{kind} {tool_name}".casefold():
        print("  [permission] -> REJECTED by policy")
        return PermissionDecisionReject(
            feedback="Destructive operations are not permitted in this demo."
        )

    print("  [permission] -> approved once")
    return PermissionDecisionApproveOnce()
```

Python の利点は、**`GHCP001` の抑制が不要**なことです。.NET プロジェクトでは権限判定を使うために、試験的 API に関するビルドエラーを抑制する必要があります。Python では `copilot.rpc` から直接公開されており、追加の明示的な有効化は不要です。

⚠️ 権限ハンドラーには注意点があります。このハンドラーは **カスタムツール** に対しては発火し、ラボ 03 のツールでも必要です。一方、シェルコマンドでは発火しないことが確認されています。権限診断を実行すると、モデルは `echo` を実行して出力を返しましたが、`[permission]` 行は表示されませんでした。これはホスト側の Copilot CLI がすでにシェル実行を許可しているためです。

`on_permission_request` は一般的な強制ポイントではなく、カスタムツール用のポリシーフックとして扱ってください。依存する前に、**自分の**環境で本当に発火することを確認してください。

参照コードは
[`sdk_labs/permissions_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/permissions_sample.py)
にあります。shell hook による governance の代替については、
[extra-governance-hooks](../../labs/extra-governance-hooks/)
を参照してください。

## ステップ 9 — 試してみる

存在しない顧客、たとえば `C999` を試してください。`tools_sample.py` のプロンプトを次のように変更します。

```python
await session.send(
    "How much has customer C999 spent in total? Use the available tool."
)
```

サンプルを再実行し、アシスタントが取引を見つけられなかったことを報告するか確認してください。

次に、小売データを必要としないプロンプトを試してください。

```python
await session.send("In one short sentence, define average order value.")
```

モデルは直接回答するはずです。顧客の検索が不要なので、`[tool]` 行は表示されないはずです。

## ✅ チェックポイント

ここまでで、次の内容を説明できるようになります。

- [x] 動的データをシステムメッセージに詰め込むより、ツールのほうが優れている理由
- [x] `@define_tool(description=...)` が Python のツールをどう説明するか
- [x] Pydantic の `Field(description=...)` がツール パラメーターをどう説明するか
- [x] `tools=[get_customer_total]` によって関数がモデルから利用可能になる仕組み
- [x] Python のカスタムツールに `on_permission_request` が必要な理由
- [x] Python のイベントが `evt.type` で分岐する理由
- [x] 実際に動かすホスト上で権限フックを検証しなければならない理由

## 💡 追加課題

customer が購入した product category を返す 2 つ目のツールを追加してください。たとえば `C003` なら `Electronics` と `Fashion` です。

2 つ目の Pydantic params model を使うか、`GetCustomerTotalParams` を再利用し、ツールに正確な説明を付けて `get_customer_total` と並べて登録したうえで、次のように質問してください。

```text
Which categories has customer C003 bought from, and how much have they spent?
```

モデルが 1 つのツールだけを呼ぶのか、両方のツールを呼ぶのか、それとも直接回答するのかを確認してください。

## 関連資料

- 前へ: [ラボ 02 — 最初のストリーミング チャット](../02-first-chat/)
- 次へ: [ラボ 04 — イベント](../04-events/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
- [追加ラボ — ガバナンス フック](../../labs/extra-governance-hooks/)
