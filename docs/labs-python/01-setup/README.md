# ラボ 01 — セットアップ

**目的:** Copilot SDK 向けの Python トラックをセットアップします。SDK のセッション、
ストリーミング、サンプルを実行するための土台として、Agent HQ デモ アプリを使います。

**所要時間:** 約15分

## 前提条件

ラボで必要なのは実装トラックのどちらか一方だけです。このページでは
`src/AgentOrchestrator-python/` 配下の Python 実装を使います。.NET トラックは
`src/AgentOrchestrator/` 配下にあります。

開始前に次をインストールしてください。

- **Python 3.11 以降**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**
  依存関係の管理とコマンド実行に使います
- **[GitHub Copilot CLI](https://github.com/github/copilot-cli)**
  サインイン済みである必要があります
- `git`, `curl`, `jq`

⚠️ このトラックでは .NET SDK は **不要** です。Python SDK パッケージは
`github-copilot-sdk` のバージョン **1.0.9** で、`copilot` としてインポートします。
このプロジェクトでは
[`pyproject.toml`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/pyproject.toml)
でバージョンを固定しています。

## ステップ 1 — クローンして確認する

```bash
git clone https://github.com/vicperdana/aigenius-copilotsdk-s5ep2.git
cd aigenius-copilotsdk-s5ep2
```

Python 実装は .NET 実装と並んで配置されています。

```text
src/AgentOrchestrator-python/
```

全体像を把握したい場合は、Python トラックの概要を読んでください。

[`src/AgentOrchestrator-python/README.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md)

.NET アプリと機能単位で対応しており、API コントラクト、初期データ、意図的に残した
コードスメル、Copilot SDK の学習ルートが共通です。

⚠️ **トラックは 1 つ選んでください。** Python でも .NET でも進められ、両方を
インストールする必要はありません。ポートが重ならないため同時実行も可能です。
.NET は 5050 と 5051、Python は API と UI の両方で **5070** を使います。

## ステップ 2 — 依存関係を復元する

リポジトリ ルートから実行します。

```bash
cd src/AgentOrchestrator-python
uv sync
```

`uv sync` は仮想環境を作成し、アプリケーション依存関係、開発用依存関係、FastAPI、
SQLModel、pytest、ruff、Copilot SDK をインストールします。

⚠️ 後続の Python コマンドは、コマンド自体がディレクトリを変更しない限り、
`src/AgentOrchestrator-python` から実行してください。ソリューションファイルはなく、
ルート レベルで実行できる Python パッケージもありません。

## ステップ 3 — テストを実行する

```bash
uv run pytest
```

より簡潔な CI 風チェックはこちらです。

```bash
uv run pytest -q
```

期待される結果は、30 個のテストがすべて成功することです。ある検証済みの実行結果は次のとおりです。

```text
..............................                                           [100%]
30 passed in 0.61s
```

内訳は 14 個のドメインテストと 12 個の MCP サーバーテストで、どちらも .NET スイートと
1 対 1 で対応しています。これに加えて、ブラウザーと API 間のリクエスト形式を守る
Python 専用のコントラクトテストが 4 個あります。

この数は覚えておいてください。後続のラボでは、この 30 テストを壊さずに挙動を拡張することが求められます。

## ステップ 4 — リンターを実行する

```bash
uv run ruff check .
```

期待される出力は次のとおりです。

```text
All checks passed!
```

リンターの設定は `pyproject.toml` にあります。

## ステップ 5 — API と UI を起動する

1 つ目のターミナルで実行します。

```bash
uv run uvicorn app.main:app --port 5070
```

<http://localhost:5070> を開いてください。空のチャット UI が表示されるはずです。

![空の状態の Retail Analytics Assistant チャット UI。暗い色のヘッダーがあり、
モデルのドロップダウンは Claude Haiku 4.5 に設定されています。歓迎メッセージの見出し、
5 つのリテール向け質問候補、そして下部にメッセージ入力欄があります。](../../screenshots/python-chat-ui-empty.png)

⚠️ .NET トラックとは異なり、**UI 専用の別サーバーはありません**。FastAPI が
REST API、チャット ストリーム、静的 HTML、JavaScript を同じプロセスで提供し、
ポート 5070 で動作します。

💡 **なぜ 5060 ではなく 5070 なのですか。** Chrome、Edge、Firefox は 5060 番ポートへの
アクセスを遮断します。これは SIP ポートで、ブラウザーの遮断対象ポート一覧に含まれているためです。
その結果、`curl` では問題なくても、ページは `ERR_UNSAFE_PORT` で失敗します。
ポートを変更する場合は、5060、5061、6000 を避けてください。

編集しながらの再読み込み開発では、`--reload` を追加してください。

```bash
uv run uvicorn app.main:app --port 5070 --reload
```

⚠️ **ポートがすでに使用中ですか。** 以前の実行で起動したサーバーが生き残っていて、
古いコードを配信している可能性があります。再起動前に 5070 を listen しているプロセスを停止してください。

## ステップ 6 — 正常性確認エンドポイントを確認する

2 つ目のターミナルで、引き続き `src/AgentOrchestrator-python` から実行します。

```bash
curl http://localhost:5070/api/chat/health
```

期待される出力は次のとおりです。

```json
{"status":"healthy","service":"CopilotChat","availableModels":["claude-haiku-4.5","gpt-4.1","gpt-5","claude-sonnet-4.5","claude-opus-4.5","gemini-2.5-pro"]}
```

このエンドポイントはモデルを呼び出しません。アプリケーションが起動していることを確認し、
モデル一覧の動的な取得に失敗した場合に使う静的なフォールバックカタログを表示します。

## ステップ 7 — REST API を確認する

Python API は .NET と同じ camelCase の JSON コントラクトを維持しています。つまり、
Python 内部の `customer_id`、`product_category`、`top_features` ではなく、
`customerId`、`productCategory`、`topFeatures` を使います。

次を実行します。

```bash
curl -s http://localhost:5070/api/transactions | jq 'length'
curl -s http://localhost:5070/api/segments | jq 'length'
curl http://localhost:5070/api/segments/predict/C003
```

期待されるポイントは次のとおりです。

- `GET /api/transactions` は 10 行を返します
- `GET /api/segments` は 4 行を返します
- 予測の呼び出しは次を返します

```json
{"customerId":"C003","predictedSegment":"High Value","confidence":0.89,"topFeatures":["high_total_spend","multi_category","total_1700"]}
```

この camelCase コントラクトは
[`app/models.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/models.py)
で実装されているため、同じ `curl` の例を両トラックで利用できます。

## ステップ 8 — ストリーミングが動くことを確認する

これにより、Copilot SDK の接続が正しく行われ、CLI にサインイン済みであり、
API がモデル出力をブラウザーまたはターミナルへ逐次返せることを確認できます。

```bash
curl -sN -X POST http://localhost:5070/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with exactly: streaming works","model":"claude-haiku-4.5"}'
```

期待されるストリーム形式は次のとおりです。

```text
data: {"content": "streaming works"}

data: [DONE]
```

重要なのは 3 点です。各イベントは `data: ` で始まり、各イベントの後には空行が入り、
最後は `data: [DONE]` で終わります。

⚠️ フィールド名は `message` ではなく `prompt` です。認識されないキーは黙って無視されるため、
入力を誤ると空のプロンプトが送られ、エラーではなく汎用的なあいさつが返ってきます。

⚠️ 代わりに `data: {"error": "..."}` が見えた場合は、サーバーは SDK まで到達したものの、
SDK がリクエストを完了できなかったことを意味します。よくある原因は、Copilot CLI にサインインしていないことや、
アカウントで利用できないモデルを選んでいることです。

## ステップ 9 — SDK ラボ サンプルを確認する

以降の Python SDK ラボではすべて `sdk_labs` モジュールを使います。ここで実際のサンプルを 1 つ実行してください。

```bash
uv run python -m sdk_labs tools
```

期待される出力は次のとおりです。

```text
== Lab 03: tools ==

Model: claude-haiku-4.5
Prompt: How much has customer C003 spent in total?

  [tool] get_customer_total(C003) -> $1,700.00

Assistant: Customer C003 has spent a total of **$1,700.00** across 2 transactions.
```

コマンド ディスパッチャーは
[`sdk_labs/__main__.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/__main__.py)
にあります。後続のラボでは `uv run python -m sdk_labs events`、
`uv run python -m sdk_labs sessions`、`uv run python -m sdk_labs mcp` を使います。

## ステップ 10 — UI を試す

ブラウザーで <http://localhost:5070> に戻り、**Model** ドロップダウンを開いて
メッセージを送信し、SSE の描画経路を確認してください。

💡 リクエスト本文は `ChatRequest` に合わせて `prompt` を使います。以前の版ではここで
`message` を送っていましたが、Pydantic は未知のキーを破棄するため、UI は空のプロンプトに対する
応答をストリームし、目立った失敗にはなりませんでした。現在は
`tests/test_chat_contract.py` で、`app.js` が送るフィールドと API が読むフィールドが一致することを検証しています。

## ✅ チェックポイント

ここまでで、次の状態になっているはずです。

- [x] `uv sync` で Python の依存関係を復元できている
- [x] 30/30 のテストが成功している
- [x] Ruff が成功している
- [x] API と UI がポート 5070 で一緒に動作している
- [x] REST エンドポイントが初期投入済みの camelCase データを返している
- [x] 実際のモデルから動的なストリーミング応答を受け取れている
- [x] `uv run python -m sdk_labs ...` で SDK ラボ サンプルを実行できる

## 💡 追加課題

モデル一覧のエンドポイントを問い合わせて、アカウントで利用できる件数を数えてください。

```bash
curl -s http://localhost:5070/api/chat/models | jq 'length'
```

次に、
[`app/routers/chat.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py)
にあるフォールバックカタログを確認してください。信頼できる情報源はライブリストであり、
静的リストがフォールバックにすぎない理由はラボ 02 で説明します。

## 関連資料

- 次へ: [ラボ 02 — 最初のチャット](../02-first-chat/)
- [デモ: Copilot SDK の組み込み](../../demos-python/01-copilot-sdk-integration.md)
- [トラブルシューティング](../../breakouts/troubleshooting.md)
