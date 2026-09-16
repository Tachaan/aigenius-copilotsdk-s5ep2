# ラボ 05 — セッション

**目的:** 会話に安定した識別子を与えてプロセスの再起動後も維持できるようにし、セッションの永続化によって何が得られ、何は得られないのかを理解します。

**所要時間:** 約20分です。

**前提条件:** [ラボ 04](../04-events/) を完了していること。

## ステップ 1 — 問題を理解する

ここまではすべて状態を保持しない処理でした。各実行は新しいセッションを作成し、プロンプトを送り、その文脈を破棄します。プロセスを再起動すると、モデルは何を話していたかをまったく覚えていません。

これは単発のサンプルとしては問題ありませんが、実際のアシスタントとしては役に立ちません。3 回続けて質問したリテールアナリストは、4 回目の質問でも同じ顧客の話が続いていることを期待します。

## ステップ 2 — セッションのサンプルを実行する

```bash
cd src/AgentOrchestrator-python
uv run python -m sdk_labs sessions
```

モデルを上書きするには `--model <id>` を付けます。

```bash
uv run python -m sdk_labs sessions --model gpt-5-mini
```

確認済みの出力は次のとおりです。

```text
== Lab 05: sessions ==

Model: claude-haiku-4.5
Session id: sdklabs-75e6b8f216d0451b

--- Turn 1 (new session) ---
You: Remember this: my favourite retail segment is 'At Risk'. Reply with just OK.
Assistant: OK

Session closed.

--- Turn 2 (resumed session) ---
You: Which retail segment did I say was my favourite?
Assistant: Your favourite retail segment is 'At Risk'.

--- Session metadata ---
  id=sdklabs-75e6b8f216d0451b metadata retrieved
```

セッション ID は実行ごとにランダムなので、あなたの値は異なります。重要なのは ID の値そのものではなく、*最初のセッションを閉じたあとでも* 2 回目のやり取りで `'At Risk'` を覚えていたことです。

この実行で確認できるのは、1 つのプロセス内で、破棄したセッションを再開できることです。これだけでは、デバイス間の引き継ぎや再起動後の復旧までは確認できません。

## ステップ 3 — セッションに ID を与える

[`sessions_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/sessions_sample.py)
を開いてください。最初のやり取りでは明示的な `session_id` を渡しています。

```python
session_id = f"sdklabs-{uuid.uuid4().hex}"[:24]

session = await client.create_session(
    session_id=session_id,
    model=model_id,
    streaming=False,
)
async with session:
    await send_and_print(
        session,
        "Remember this: my favourite retail segment is 'At Risk'. Reply with just OK.",
    )
```

この ID が、このラボの残りすべての鍵になります。これがなくても SDK はセッションを作成しますが、あとから戻るための手掛かりがありません。

その後、`async with session:` ブロックがセッションを閉じます。次のやり取りは、実行中のオブジェクトを継続するのではなく、閉じたセッションを実際に再開するものです。

## ステップ 4 — セッションを再開する

2 回目のターンでは、同じ ID を別の SDK 呼び出しに渡します。

```python
resumed = await client.resume_session(session_id, model=model_id, streaming=False)
async with resumed:
    await send_and_print(resumed, "Which retail segment did I say was my favourite?")
```

💡 **これは .NET の同等処理よりも単純です。** C# では `ResumeSessionConfig` を構築し、必須の第 2 引数として渡す必要があります。省略するとコンパイルエラーになります。Python には `ResumeSessionConfig` がなく、通常のキーワード引数として同じ設定を渡せます。位置引数なのは `session_id` だけです。

```python
await client.resume_session(session_id)                       # valid
await client.resume_session(session_id, model="gpt-5")        # valid
await client.resume_session(session_id, streaming=False)      # valid
```

⚠️ **ここでは `session_id` は位置引数ですが、作成時にはキーワード引数です。** `create_session(session_id=...)` と `resume_session(session_id)` の非対称性に注意してください。`resume_session` では、セッション ID の後ろはすべてキーワード専用です。

この確認をより確かなものにするには、最初の実行で表示された ID を使って、**2 つ目のプロセス**で再開処理を実行してください。

```bash
uv run python -m sdk_labs sessions --resume sdklabs-75e6b8f216d0451b
```

これで実際にプロセス境界をまたぐことになります。別のマシンから再開するには、さらに同じセッション永続化ストアへのアクセス、互換性のある実行環境、そして適切な認可が必要です。

## ステップ 5 — 保存済みセッションを見つける

このサンプルでは、SDK にメタデータも問い合わせています。

```python
metadata = await client.get_session_metadata(session_id)
```

戻り値は `SessionMetadata | None` です。一致する保存済みセッションがない場合は `None` になるため、使う前に確認してください。

```python
print(
    "  (no metadata returned)"
    if metadata is None
    else f"  id={session_id} metadata retrieved"
)
```

既知の ID から始める代わりに、保存済みセッションを一覧したい場合は `list_sessions` を使います。

```python
sessions = await client.list_sessions()          # -> list[SessionMetadata]
```

よくあるパターンは次のとおりです。

1. サインインしているユーザーのセッションを一覧します。
2. ユーザーに 1 つ選んでもらうか、最新のものを選択します。
3. その ID を `resume_session(id, ...)` に渡します。

## ステップ 6 — アーキテクチャと結び付ける

セッションの永続化によって、次が可能になります。

- **デバイスやクライアントをまたぐ引き継ぎ** — ある場所で開始し、別の場所で続きを行えます。
- **クラッシュからの復旧** — プロセスの再起動後に、文脈をゼロから作り直さず再開できます。
- **監査可能性** — 安定した ID があることで、会話の調査、整理、追跡がしやすくなります。

現在のデモアプリでは、ブラウザーがチャット履歴を `localStorage` に保持しています（[`app.js`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js) を参照）。これは 1 台のデバイス上の 1 つのブラウザーでは機能しますが、会話を別の場所へ持ち出すことはできません。スマートフォンでアプリを開くと、履歴はありません。

この問題を解決するのが SDK セッションです。UI は会話全体ではなくセッション ID を保存でき、同じセッションストアを使う認可済みクライアントなら、同じサーバー側セッションを再開できます。

⚠️ **セッション ID はアクセス制御ではありません。** ID は秘密情報や権限そのものではなく、識別子として扱ってください。保存済みの会話を再開する前に、アプリ側では通常どおりユーザー認証と認可が必要です。

Python トラックでは、PyPI の `github-copilot-sdk` **1.0.9** にバージョンを固定し、`copilot` としてインポートしています。また、Python 3.11 以降が必要です。これらの要件は [`pyproject.toml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/pyproject.toml) で確認できます。

## ⚠️ 落とし穴

- **ID の衝突:** セッション ID はキーです。同じ ID を再利用すると、新しい会話が作られるのではなく、古い会話が再開されます。
- **不透明な ID:** ランダムな ID はデモには向いていますが、実システムではユーザー、案件、ワークフローに対応付けられる必要があります。
- **ID は権限ではありません:** ID を知っている、または推測できるだけで会話にアクセスできてはいけません。認可は別に実装してください。
- **ID に機密データを含めないでください:** セッション ID にトークン、メールアドレス、顧客情報を入れてはいけません。
- **メタデータが必ずあると思わないでください:** `get_session_metadata` は未知の ID に対して `None` を返すため、参照前に確認してください。
- **クローズを忘れないでください:** このサンプルでは `async with` を使っているため、1 回目のやり取りは 2 回目で再開する前に確実に閉じられています。これを省くと、何も確認できません。

## 💡 追加課題

1. メタデータの取得後に 3 回目のやり取りを追加し、同じ ID で再開して、元の `'At Risk'` メッセージについて別の質問をしてください。
2. 2 つ目のターミナルから `--resume` の処理を実行し、自分でプロセスをまたいだ再開を確認してください。
3. 保存済みセッションを一覧し、最新のものを再開してください。

   ```python
   sessions = await client.list_sessions()
   if sessions:
       resumed = await client.resume_session(sessions[0].id, model=model_id)
   ```

4. ID を `"analyst-demo"` のような安定した文字列に変更し、サンプルを再実行すると 1 つの会話が長期間継続されることを観察してください。

## ✅ チェックポイント

ここまでで、次の内容を説明できるようになります。

- [x] 永続化しないとプロセスの再起動で文脈が失われる理由
- [x] `create_session(session_id=...)` がアプリに安定したキーを与える仕組み
- [x] Python の `resume_session(id, ...)` は .NET のような別個の設定オブジェクトを必要とせず、通常のキーワード引数を受け取ること
- [x] `get_session_metadata` と `list_sessions` が保存済みセッションの発見にどう役立つか、そしてメタデータが `None` になりうること
- [x] SDK セッションがデバイス間でチャット履歴を引き継ぐための適切な基盤である理由
- [x] プロセス間やデバイス間での再開が、共有ストレージ、互換性のある実行時動作、認可にも依存する理由

## 関連資料

- 前へ: [ラボ 04 — イベント](../04-events/)
- 次へ: [Lab 06 — MCP](../06-mcp/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
