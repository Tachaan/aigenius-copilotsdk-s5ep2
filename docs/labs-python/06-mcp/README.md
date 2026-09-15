# ラボ 06 — MCP

**目的:** Model Context Protocol サーバーへ接続し、自分で実装していないツールを利用する方法と、同じくらい重要な、そのツールが実際に使われたことを証明する方法を学びます。

**所要時間:** 約20分

**前提条件:** [ラボ 05](../05-sessions/) を完了しており、HTTP MCP サーバーにアクセスするためのインターネット接続があること。

## ステップ 1 — MCP が必要な理由

[ラボ 03](../03-tools/) では `@define_tool` を使ってツールを書きました。機能が自分のコードベース内にある場合は、それが適切なやり方です。

MCP は別のケースのためにあります。つまり、誰かがすでに構築して実行している機能を使いたい場合です。自分で統合を書いて保守する代わりに、標準プロトコルに対応したサーバーへセッションを接続すると、モデルからそのツール群を利用できるようになります。

このラボでは **Microsoft Learn** の MCP サーバーを HTTP 経由で使います。これはこのリポジトリがすでに VS Code 用に設定しているものと同じなので、追加でインストールするものはありません。

## ステップ 2 — サーバーを設定する

[`mcp_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/mcp_sample.py) を開き、セッション設定を見つけてください。

```python
        session = await client.create_session(
            model=model_id,
            streaming=False,
            mcp_servers={
                "microsoft.docs.mcp": {
                    "type": "http",
                    "url": "https://learn.microsoft.com/api/mcp",
                    "tools": ["*"],
                }
            },
            on_permission_request=PermissionHandler.approve_all,
        )
```

💡 **ここでの API は通常の辞書です。** `MCPServerConfig` はインスタンス化するクラスではなく、複数の `TypedDict` 型を組み合わせたユニオン型です。.NET SDK では `IDictionary<string, McpServerConfig>` が必要で、型の緩い辞書はコンパイル時に拒否されます。一方、Python では辞書リテラルをそのまま渡せます。

このユニオン型には 2 つの形式があります。

| 形式 | 必須フィールド | 使用する場面 |
|:------|:----------------|:---------|
| `MCPHTTPServerConfig` | `type` (`"http"` または `"sse"`)、`url`、`tools` | サーバーにネットワーク経由で到達できる場合 |
| `MCPStdioServerConfig` | `command`、`tools` | サーバーをローカルのサブプロセスとして実行する場合 |

⚠️ **`tools` は省略不可で必須です。** サーバーが公開するすべてを許可するなら `["*"]` を使い、範囲を狭めるなら特定のツール名を列挙してください。このキーを省くと型エラーになります。

💡 **stdio 形式では `type` は省略可能です。** CLI は `command` があることで stdio だと推論し、`url` があることでリモートサーバーだと推論します。stdio 側の任意キーは `args`、`env`、`timeout`、`working_directory` です。最後のキーは **`cwd` ではなく `working_directory`** であることに注意してください。SDK は通信形式へ変換する際にこれを `cwd` にリネームするため、今は `cwd` を直接渡してもたまたま動きますが、型付きの公開 API ではありません。

⚠️ **`on_permission_request` もここで重要です。** [ラボ 03](../03-tools/) と同様に、Python ではハンドラーを渡さないとツール呼び出しは拒否されます。`PermissionHandler.approve_all` はラボ用途なら問題ありませんが、実データに触れる用途では適切ではありません。

## ステップ 3 — 実行する

```bash
cd src/AgentOrchestrator-python
uv run python -m sdk_labs mcp
```

モデルを上書きしたい場合は `--model <id>` を追加します。

```bash
uv run python -m sdk_labs mcp --model gpt-5-mini
```

確認済みの出力例は次のとおりです。

```text
== Lab 06: mcp ==

Model: claude-haiku-4.5
Prompt: asking the model to consult Microsoft Learn docs

  [mcp] session.mcp_server_status_changed
  [mcp] session.mcp_servers_loaded
  [mcp] session.mcp_server_status_changed
  [tool-request] assistant.message: microsoft.docs.mcp/microsoft_docs_search
  [tool] tool.execution_start: microsoft.docs.mcp/microsoft_docs_search
  [tool] tool.execution_complete: microsoft.docs.mcp/microsoft_docs_search (success=True)

Assistant: Let me fetch the main Azure Container Apps documentation page for a clearer overview:
  [tool-request] assistant.message: microsoft.docs.mcp/microsoft_docs_fetch
  [tool] tool.execution_start: microsoft.docs.mcp/microsoft_docs_fetch
  [tool] tool.execution_complete: microsoft.docs.mcp/microsoft_docs_fetch (success=True)

Assistant: **Azure Container Apps** is a serverless platform for running containerized applications without managing underlying infrastructure—you provide your container, and Azure handles the servers, orchestration, and deployment. It automatically scales based on demand (HTTP traffic, events, or resource load) and supports microservices, APIs, background jobs, and event-driven workloads with built-in features like traffic splitting, secrets management, and HTTPS ingress.

✅ MCP tool(s) invoked: microsoft.docs.mcp/microsoft_docs_fetch, microsoft.docs.mcp/microsoft_docs_search
```

実際に 2 つの MCP ツールが実行されています。関連ページを見つけるための `microsoft_docs_search` と、そのうち 1 ページを読むための `microsoft_docs_fetch` です。最後の行がその事実を確認しており、サンプルは**終了コード 0** で終了します。

💡 **.NET トラックでは異なる結果が記録されています。** その実行では Learn サーバー自体は読み込まれましたがツールが公開されず、モデルは組み込みの `web_fetch` にフォールバックして、サンプルは 0 以外の終了コードで終了しました。同じサーバー、同じプロトコルでも結果が異なります。まさにそれが次のステップが必要な理由です。

## ステップ 4 — ツールが実際に使われたことを証明する

ここがこのラボの本質です。Azure Container Apps は公開情報なので、モデルは **MCP ツールをまったく呼ばなくても**、確信を感じさせるもっともらしい回答や、引用付きの正しい回答を生成できます。良い回答であることは、ツールを使った証拠にはなりません。

このサンプルは、実際の証拠になるイベントを購読しています。

- `session.mcp_servers_loaded` — 設定が受理されたことを示します
- `session.mcp_server_status_changed` — サーバー接続の状態が変化したことを示します
- `mcp.tools.list_changed` — サーバーがツール一覧を公開したことを示します
- `external_tool.requested` — アシスタントが外部ツールを要求したことを示します
- `tool.execution_start` / `tool.execution_complete` — ツールが実際に実行されたことを示します

重要なのは、どのようにしてそのツール実行が *MCP* 由来だと判定されるかです。`tool.execution_start` には `mcp_server_name` が含まれており、それが設定されている実行だけがカウントされます。

生成される `ToolExecutionStartData` には `tool_call_id`、`tool_name`、`arguments`、`mcp_server_name`、`mcp_tool_name` などのフィールドがあります。MCP 固有のフィールドがあることだけが、そのツールが設定済みの MCP サーバーから来たことの証明になります。

```python
                    # Only a tool carrying an MCP server name came from MCP.
                    # Built-ins such as web_fetch must not count, or an
                    # unreachable server still reports success.
                    if evt.data.mcp_server_name:
                        mcp_tools.add(tool_name)

                    invoked_tools.add(tool_name)
```

MCP 由来のツールが 1 つも実行されなかった場合、サンプルはそのことを表示して 0 以外の終了コードで終了します。

```python
    if not mcp_tools:
        print()
        print("⚠️  No MCP tool was invoked.")
        if invoked_tools:
            print(f"    The model used non-MCP tool(s) instead: {', '.join(sorted(invoked_tools))}")
        print("    The answer may have come from the model's own knowledge or a built-in")
        print("    tool rather than Microsoft Learn. Check the server is reachable and that")
        print("    its tools were loaded — look for the [mcp] lines above.")
        return 1
```

⚠️ **誤ったものを数えるくらいなら、確認しないほうがまだましです。** 以前のバージョンでは *任意の* ツール実行を数えてしまい、MCP とは無関係な `web_fetch` を使った場合でも `✅ MCP tool(s) invoked: web_fetch` と表示していました。MCP と無関係なツールなのに成功扱いしていたわけです。これは壊れた統合に対して誤った安心感を作ってしまいます。

💡 接続しないサーバーのデバッグをしたい場合は、`SDKLABS_TRACE_EVENTS=1` を設定すると、MCP 関連イベントだけでなくすべてのイベントを出力できます。

```bash
SDKLABS_TRACE_EVENTS=1 uv run python -m sdk_labs mcp
```

## ステップ 5 — エディター設定と比較する

このリポジトリは、同じサーバーを VS Code 用に [`.vscode/mcp.json`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.vscode/mcp.json) ですでに設定しています。

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

このファイルはエディター用です。一方 `mcp_servers=` 引数は、アプリやサンプル内部で動いている Copilot SDK セッション用です。利用者は違っても、サーバーとプロトコルは同じです。

これが MCP の要点です。1 つのプロトコルを、多くのクライアントで使えます。同じツールサーバーを、エディター、CLI、テストハーネス、あるいはアプリケーションエージェントから利用できます。

頭の中ではこの 2 つの設定を分けて考えてください。エディターの MCP 設定は開発ツールを助けるためのものであり、`mcp_servers=` はこの SDK セッションがモデルに対して何を提供できるかを変えます。

## ステップ 6 — MCP を *使う* 側と *提供する* 側

ここまではすべて、誰かのサーバーをセッションから利用する話でした。このリポジトリ自身も MCP サーバーを 1 つ **実装** しており、その理由を理解しておく価値があります。

これまでは `CopilotChatService` がアプリ自身のデータにアクセスできないまま、プロンプトをモデルへ送っていました。たとえばチャットに「最も多く支出している顧客は誰ですか？」と聞いても、リテール用データベースが見えていないので推測するしかありませんでした。

[`mcp_server/`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py) は、`retail.db` に対する 5 つの読み取り専用ツールでそのギャップを埋めます。

| ツール | 答えられること |
|:-----|:--------|
| `list_transactions` | 「C003 の最近の購入を見せて」 |
| `get_transaction` | 「取引 7 は何ですか？」 |
| `list_segments` | 「どんなセグメントがありますか？」 |
| `get_customer_summary` | 「C001 は合計いくら使っていますか？」 |
| `predict_segment` | 「C003 はどのセグメントに属しますか？」 |

[`copilot_chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py) は、前の表で示した stdio 形式としてこれを接続しています。

```python
{
    "retail-analytics": {
        "command": sys.executable,      # same interpreter as the API
        "args": ["-m", "mcp_server"],
        "working_directory": str(PROJECT_ROOT),
        "tools": ["*"],
    }
}
```

ここでの本当の学びは、次の 2 つの設計判断です。

**1. 最小権限はコード上の約束ではなく、接続レベルで実現します。** エンジンは SQLite を `mode=ro` で開くため、書き込みはドライバーで拒否されます。

```python
create_engine("sqlite:///file:" + str(path) + "?mode=ro&uri=true")
```

プロンプトに紛れ込んだ指示であってもデータを変更できません。なぜなら、その権限自体が最初から与えられていないからです。これに対して「単に INSERT 文を書いていないだけ」というのは、制御ではなく慣習にすぎません。

**2. 生の SQL ではなく、ドメインツールを公開します。** モデルに渡すのは `run_query` ではなく `get_customer_summary` です。汎用の SQLite MCP サーバーを使えばコードはゼロで済みますが、その代わりモデルに任意 SQL の抜け道を渡すことになります。ツール面そのものがセキュリティ境界なので、小さく具体的に保つべきです。

ここで **変わっていない** 点にも注意してください。REST API は依然として `RetailAnalyticsService` を通じてデータベースへ直接アクセスします。MCP は *モデル* のためのものであり、アプリケーション自身のデータベースアクセスに使うものではありません。自分の CRUD を LLM ツールプロトコル経由にすると、サブプロセスのホップが 1 つ増えるだけで、トランザクションと型安全性を失う割に得るものがありません。

試してみてください。

```bash
cd src/AgentOrchestrator-python
uv run uvicorn app.main:app --port 5070
```

```bash
curl -s -X POST http://localhost:5070/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is customer C003 total spend and which segment are they in?"}'
```

ステップ 4 と同じように、証拠は API ログに出ます。

```
INFO:app.services.copilot_chat:MCP tool call: retail-analytics/get_customer_summary
INFO:app.services.copilot_chat:MCP tool call: retail-analytics/predict_segment
```

💡 **権限ハンドラーは無条件ではなくスコープ付きです。** `approve_all` はコンソールラボなら問題ありませんが、このサービスはブラウザーから到達できるため、`retail-analytics` の読み取り専用ツールだけを許可し、それ以外は拒否しています。

```python
if (
    isinstance(request, PermissionRequestMcp)
    and request.server_name == RETAIL_MCP_SERVER
    and request.read_only
):
    return PermissionDecisionApproveOnce()
```

## ⚠️ 落とし穴

- 両方の設定形式で **`tools` は必須** です。すべて許可するなら `["*"]` を使ってください
- **`on_permission_request` を省略すると**、Python ではツール呼び出しが拒否されます
- Learn サーバーには**ネットワーク越しに接続**します。到達できない場合、モデルには MCP ツールがなく、自前の知識だけで回答することがあります。そのため、0 以外の終了コードで失敗を示す必要があります
- **もっともらしい回答は証拠ではありません。** `tool.execution_start` に付く `mcp_server_name` だけが、MCP ツールが実行された証拠です
- **MCP サーバーはサードパーティーコード** であり、強力な権限を公開し得ます。実運用を扱うエージェントから参照させる前に、サーバー、権限、データアクセスを必ず精査してください
- stdio 設定では **`cwd` ではなく `working_directory`** を使います。SDK 側でリネームされ、型チェックされるのは公開キーだけです
- **読み取り専用という*ヒント*は、読み取り専用の*保証*ではありません。** `read_only_hint` はホストに自動承認してよいと伝えるだけです。`mcp_server/` で実際に書き込みを止めているのは `mode=ro` の SQLite 接続です

## 💡 発展課題

1. `tools` を `["*"]` から 1 つのツール名に絞り、モデルがどう適応するか観察してください
2. 2 つ目の MCP サーバーを追加し、モデルがツールセット間でどう選ぶか比較してください
3. `disabled_mcp_servers=[...]` でサーバー名を渡して同じプロンプトを再実行し、Learn ツールあり・なしで回答を比較してください
4. HTTP 設定を、手元の任意のローカル MCP サーバーに対する stdio 設定 `{"type": "stdio", "command": "...", "tools": ["*"]}` に差し替えてください
5. 認証付きまたはより高度な MCP シナリオとして、`mcp_oauth_token_storage`、`github_mcp_tool_config`、`enable_mcp_apps` を確認してください
6. `PermissionHandler.approve_all` を、モデルに使わせたくないツールを記録して拒否するハンドラーに置き換えてください

## ✅ チェックポイント

次の内容を説明できるようになっているはずです。

- [x] MCP がラボ 03 で自分で書いたツールとどう違うか
- [x] HTTP 設定形式と stdio 設定形式をいつ使い分けるか
- [x] `mcp_servers` が通常の辞書を受け取るのは設定が `TypedDict` だからであり、`tools` が必須であること
- [x] もっともらしい回答が、MCP ツールが呼ばれた証拠にはならない理由
- [x] `mcp_server_name` によって、本物の MCP ツールと組み込みツールをどう見分けるか
- [x] `.vscode/mcp.json` と SDK 設定が同じサーバーを対象にしていること
- [x] このリポジトリが MCP サーバーを *利用* するだけでなく *提供* もしている理由と、それでも REST API が依然としてデータベースと直接やり取りする理由
- [x] `mode=ro` が実際の制御であり、`read_only_hint` は単なるヒントにすぎない理由

## 関連

- 前へ: [ラボ 05 — セッション](../05-sessions/)
- 次へ: [Lab 07 — まとめ](../07-wrap-up/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
