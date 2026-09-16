# Python ラボ

**AI Genius S5E2 — Agent HQ Demo** のためのハンズオン演習です。主題は
**GitHub Copilot SDK** です。これは **Python トラック** なので、Python か
[.NET](../labs/) の **どちらか一方** を選び、順番に進めてください。
Python は **5070**、.NET は **5050/5051** を使うため、両方のスタックを同時に実行できます。

## 前提条件

| 要件 | 補足 |
|:------------|:------|
[Python 3.11+](https://www.python.org/downloads/) | `python3 --version` が `3.11` 以上を示す必要があります |
[uv](https://docs.astral.sh/uv/getting-started/installation/) | 依存関係のインストールと Python コマンドの実行に使います |
[GitHub Copilot CLI](https://docs.github.com/copilot) | Copilot を利用できる状態でサインインしている必要があります。SDK はこれと対話します |
`git`, `curl`, `jq` | `curl` と `jq` は API の確認や追加演習で使います |
ターミナルとエディター | VS Code を推奨します。このリポジトリには `.vscode/mcp.json` が含まれています |

開始前に確認してください。

```bash
python3 --version   # 3.11+
uv --version
copilot --version   # 1.x
```

基本的な Python コマンドです。アプリ ディレクトリで実行してください。

```bash
cd src/AgentOrchestrator-python
uv sync
uv run uvicorn app.main:app --port 5070   # API + UI on one port
uv run pytest                             # 30 tests
uv run ruff check .
```

## 🎯 SDK 学習ルート

中核となる学習ルートです。最初から最後まででおおよそ 2 時間です。

| # | ラボ | 実施内容 | 所要時間 |
|:--|:----|:---------------|:-----|
| 01 | [セットアップ](01-setup/) | 依存関係をインストールし、FastAPI アプリを起動して、SDK サンプルの基本動作を確認します | 約 15 分 |
| 02 | [最初のチャット](02-first-chat/) | 応答をストリーミングし、実行時にモデルを検出します | 約 20 分 |
| 03 | [ツール](03-tools/) | `@define_tool` を使って、モデルから Python を呼び出せるようにします | 約 20 分 |
| 04 | [イベント](04-events/) | 実際のセッション イベントのライフサイクルを確認します | 約 20 分 |
| 05 | [セッション](05-sessions/) | 再起動をまたいで会話を保存し、再開します | 約 20 分 |
| 06 | [MCP](06-mcp/) | MCP サーバーへ接続し、自分で実装していないツールを利用します | 約 20 分 |
| 07 | [まとめ](07-wrap-up/) | 内容を整理し、後始末をして、次に進む方向を決めます | 約 10 分 |

### 実行可能なサンプル

ラボ 03〜06 には実際の Python モジュールが対応しており、各ラボに 1 つのサブコマンドがあります。

```bash
cd src/AgentOrchestrator-python
uv run python -m sdk_labs tools
uv run python -m sdk_labs events
uv run python -m sdk_labs sessions
uv run python -m sdk_labs mcp
```

これらのサンプル コマンドは `sdk_labs` 内の実際のモジュールで動作します。モデルの応答文や
診断警告は、アカウント、SDK バージョン、ローカルの Copilot CLI 設定によって変わる場合があります。

## 📎 追加ラボ — SDK 以外

有用ではありますが、扱う内容は SDK ではなく **Copilot CLI** と一般的なアプリ開発です。
任意で実施でき、番号付きの学習ルートとは独立しています。

| ラボ | 扱う内容 | 追加扱いの理由 |
|:----|:-------|:---------------|
[API を拡張する](extra-extend-api/) | FastAPI、SQLModel、pytest | Copilot をコーディング支援として使う内容であり、SDK には触れません |
[カスタム エージェント](../labs/extra-custom-agents/) | `.agent.md` ファイル、エージェント支援レビュー | 両トラック共通の Copilot CLI 機能であり、[詳細解説](../breakouts/) に配置しています |
[ガバナンス フック](../labs/extra-governance-hooks/) | シェル フック、セキュリティ ゲート、監査ログ | Copilot CLI の機能です。SDK に対応する内容は [ラボ 03](03-tools/) にあります |

[API を拡張する](extra-extend-api/) だけが Python 固有です。カスタム エージェントと
ガバナンス フックは言語に依存しない CLI ラボなので、トラックごとに重複掲載せず、
サイトでは [詳細解説 → 追加ハンズオン](../breakouts/) にまとめています。

## この資料の約束事

- ラボ内で `cd src/AgentOrchestrator-python` と明記されていない限り、コマンドはリポジトリ ルートから **そのままコピー＆ペースト** できます
- 各ステップを確認できるように、想定出力を掲載しています
- ⚠️ は、飛ばすと問題になりやすい箇所を示します
- 💡 は、任意の追加課題を示します

## ⚠️ 何かを「直す」前に

Python 実装には、コード レビューのデモ用として、
[`app/services/retail_analytics.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py)
に **意図的に** 4 つの問題のあるコード パターンが含まれています。

- `get_transactions_with_segments` の N+1 クエリ
- `get_transaction` の `None` チェック不足
- `add_transaction` の入力検証不足
- `predict_segment` のハードコードされた閾値

.NET 側のコード スメルと完全に対応しているため、同じ解答を両トラックに適用できます。
[追加ラボ — カスタムエージェント](../labs/extra-custom-agents/) では、それらを *見つける* ことが課題です。
修正しないでください。レビュー演習は、それらが残っていることを前提にしています。
詳細は [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md) を参照してください。

## 関連資料

- [Python app README](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/README.md)
- [.NET トラック](../labs/)
- [デモ](../demos-python/) — これらのラボで触れる Python コードの解説です
- [詳細解説](../breakouts/) — アーキテクチャ、エージェント、フック、トラブルシューティングを扱います
- [トラブルシューティング](../breakouts/troubleshooting.md) — ステップが失敗した場合はまずここを確認してください
