# ラボ 07 — まとめ

**目的:** ここまでに作ったものを整理し、手元の環境を片付け、次に進むべき妥当な一歩を選べるようにします。

**所要時間:** 約10分

## ここまでで扱った内容

| ラボ | 機能 |
|:----|:-----------|
| [01](../01-setup/) | 依存関係をインストールし、FastAPI アプリを起動して SDK サンプルのスモークテストを行いました |
| [02](../02-first-chat/) | ストリーミングチャットの 1 ターンを追跡し、実行時にモデルを検出しました |
| [03](../03-tools/) | 静的なコンテキストを Python の `@define_tool` ツールに置き換えました |
| [04](../04-events/) | セッションイベントのライフサイクルと完了シグナルを観察しました |
| [05](../05-sessions/) | プロセス再起動をまたいで SDK セッションを永続化し、再開しました |
| [06](../06-mcp/) | MCP サーバーを接続して、外部ツールでエージェントを拡張しました |

任意の `extra-*` ラボは、現在はメインの SDK 学習経路の外側にあります。CLI のカスタムエージェント、ガバナンスフック、FastAPI/SQLModel の拡張練習をしたいときに使ってください。ただし SDK の流れを追ううえで必須ではありません。

## 持ち帰るべき考え方

1. **単に会話するより、組み込むほうが強いです。** SDK を使うと、エージェントはアプリケーションの一部になります。その結果、認証、ログ、デプロイパイプラインの管理下に置けます。Python では通常 `CopilotClient()` から始め、たいていは `async with CopilotClient() as client:` を使います。手動で構築する場合は、セッションを作る前に `await client.start()` を呼んでください。

2. **能力は固定せず、検出してください。** モデル一覧は `await client.list_models()` で取得するため、すべての受講者が同じプレビューモデルにアクセスできる必要はありません。

3. **セッション作成はキーワード中心です。** 何度も見てきた呼び出し形式は `await client.create_session(model=..., streaming=..., system_message=..., tools=..., mcp_servers=..., on_permission_request=...)` です。これらのキーワード専用引数が、チャット、ツール、MCP、権限の設定項目になります。

4. **文脈を詰め込むより、ツールを使うべきです。** `@define_tool` を使うと、モデルは必要な情報を必要なときに取りに行けます。事前に毎ターン推測ベースの文脈を積み込む必要がなくなり、役に立つかどうかに関係なくトークンを消費することも避けられます。Python のカスタムツールでは **必ず** `on_permission_request` が必要で、ない場合は呼び出しが拒否されます。.NET サンプルにはそのようなハンドラーは不要です。

5. **イベントはプッシュ専用です。** `session.on(handler)` はコールバックを登録し、解除用の呼び出し可能オブジェクトを返します。非同期イテレーターはないため、サンプルでは [`sdk_labs/_common.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py) の `IdleWaiter` を共有してアイドル状態またはエラーを待っています。

6. **Python 側のイベントデータクラスは 1 つだけです。** .NET はイベントのサブクラスに対してパターンマッチを使いますが、Python では `SessionEvent` が 1 種類だけで、`SessionEventType` 列挙型である `evt.type` を見て分岐します。そのためサンプルは `evt.type is SessionEventType.SESSION_IDLE` を確認しています。

7. **送信と完了待ちは別々の選択です。** `await session.send(prompt)` は送信後のイベントを自分で監視する場合に使い、`await session.send_and_wait(prompt, timeout=...)` は送信から完了待ちまでを SDK に任せる場合に使います。

8. **セッションがあるとエージェントを持ち運べます。** `resume_session` と `get_session_metadata` を使えば、プロセス再起動をまたいで状態を維持できます。デモアプリのブラウザー内 `localStorage` による履歴は便利ですが、デバイス間の移動はできません。

9. **MCP は到達範囲を広げます。** Python では MCP サーバーを通常の辞書として設定します。たとえば `mcp_servers={"microsoft.docs.mcp": {"type": "http", ...}}` のように記述し、あらゆる統合をアプリ本体に組み込む必要はありません。.NET と違って、Python では権限 API のために `GHCP001` を抑制する必要もありません。

## 後片付け

サービスを停止してください。ターミナル上で動かしているなら `Ctrl+C`、デタッチしている場合は次を使います。

```bash
lsof -ti:5070        # prints a PID if still listening
kill <PID>
```

ローカルの生成物を削除します。

```bash
rm -f src/AgentOrchestrator-python/retail.db*   # SQLite DB + WAL files
rm -f logs/*                                    # if you ran the shared CLI extras
```

`retail.db` は初回実行時に Python の作業ディレクトリに生成され、gitignore されています。⚠️ macOS ではファイルがまだ開かれていると、削除コマンドが成功したように見えてもサービスが再生成してしまうことがあります。先にサービスを止めてから生成物を削除してください。

```bash
git status --short
```

期待される状態は、出力が何もないか、意図して編集したラボファイルだけが表示されることです。ローカルのラボ作業を破棄してクリーンな checkout に戻したい場合は、次を使います。

```bash
git status
git checkout -- .        # discards uncommitted changes — irreversible
```

## 理解を確認する

1. Python トラックで `async with CopilotClient()` を使うのはなぜですか。
2. サンプルで `async for evt in session` ではなく `IdleWaiter` が必要なのはなぜですか。
3. Python のカスタムツールを `on_permission_request` なしで登録すると何が起きますか。
4. Python ではどのイベントフィールドを見ますか。また、再起動後にセッションを再開できることを示す SDK 呼び出しはどれですか。

<details>
<summary>答え</summary>

1. クライアントの開始と停止を確実に行うためです。コンテキストマネージャーを使わないなら、自分で `await client.start()` を呼び、最後に `await client.stop()` も呼ぶ必要があります。
2. SDK のイベントはプッシュ型のコールバックだからです。`session.on(handler)` はハンドラーを購読登録する方式なので、小さな `Future` ベースのヘルパーで `SESSION_IDLE` を待つか、`SESSION_ERROR` で例外を投げます。
3. ツール呼び出しは拒否されます。Python ではカスタムツールに対して権限ハンドラーが必要であり、.NET の同等サンプルにはその必要がありません。
4. すべてのイベントは `SessionEvent` なので、`SessionEventType` 列挙型である `evt.type` で分岐します。`await client.resume_session(session_id, ...)` が会話を再開し、`await client.get_session_metadata(session_id)` が保存済みメタデータを取得します。

</details>

## 次に進むなら

| 方向性 | ここから始める |
|:----------|:-----------|
| 特定の SDK サンプルを再実行する | [`sdk_labs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/__main__.py) |
| デモコードを深く理解する | [Demos](../../demos-python/) |
| トラブルシューティングとアーキテクチャを参照する | [詳細解説](../../breakouts/) |
| 自分のエージェントアプリを作る | [Copilot SDK repo](https://github.com/github/copilot-sdk) |
| 外部ツールで Copilot を拡張する | [Model Context Protocol](https://modelcontextprotocol.io/) |

### さらに進めるためのアイデア

- **サンプルをアプリに昇格させる。** `sdk_labs` のコマンドを 1 つ実際の API エンドポイントに移し、ユーザー向けの進捗表示を加えてみてください
- **会話をサーバー側で永続化する。** ブラウザーの `localStorage` を、デバイスをまたいでも履歴が残る SQLite ベースのセッションメタデータに置き換えてください
- **2 つ目の MCP サーバーを追加する。** 資格情報をソースに含めず、必要な環境変数を文書化し、ツールが実行時に現れることを証明してください
- **可観測性を強化する。** 現在は無視している event type もログに残し、本番デバッグに十分な文脈を確保しつつ、完全な prompt の保存は避けてください

## ✅ 最終チェックポイント

- [x] 7 つの SDK ラボをすべて完了した
- [x] サービスを停止し、ローカル生成物を片付けた
- [x] `git status --short` がクリーン、または意図したラボ編集だけが残っている
- [x] 上の 4 つの質問に答えられる

## 関連

- [ラボ一覧](../README.md)
- [Python app README](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
- [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md)
