# フックとガバナンス

このページでは、`.github/hooks/` 以下のガバナンスフックについて説明します。
これらのフックは Agent HQ デモに、セッションログ、ツール実行前のセキュリティゲート、
ツール実行後の監査ログ、セッションの要約を追加します。

## `retail-governance.json` のスキーマ

`.github/hooks/retail-governance.json` は、シンプルなフック構成を宣言します。

- `version`: 数値形式の構成バージョン。現在は `1` です。
- `hooks`: 各キーがライフサイクルイベント名であるマップです。
- 各イベントの値はコマンドエントリの配列です。
- 各コマンドエントリには次の項目があります。
  - `type`: 現在は `command` です。
  - `bash`: 実行するスクリプトのパスです。
  - `cwd`: コマンドの作業ディレクトリです。
  - `timeoutSec`: 最大実行時間（秒）です。

エントリの例:

```json
{
  "type": "command",
  "bash": "./.github/hooks/scripts/security-gate.sh",
  "cwd": ".",
  "timeoutSec": 15
}
```

## ライフサイクルイベント

ガバナンスファイルは、4 つのライフサイクルイベントを 4 つのシェルスクリプトに
関連付けます。

| イベント | スクリプト | 目的 |
|---|---|---|
| `sessionStart` | `.github/hooks/scripts/session-init.sh` | セッションログを初期化する |
| `preToolUse` | `.github/hooks/scripts/security-gate.sh` | ツールの使用を許可または拒否する |
| `postToolUse` | `.github/hooks/scripts/audit-logger.sh` | JSONL 監査イベントを追記する |
| `sessionEnd` | `.github/hooks/scripts/session-end.sh` | セッションの要約を書き込む |

## スクリプトの動作

### `session-init.sh`

`session-init.sh` は標準入力からフック JSON を読み取ります。`jq` で `.source`、
`.timestamp`、`.cwd` を抽出し、`logs/` を作成して、UTC 時刻、source、cwd、
現在の OS ユーザーを含む装飾付きの `SESSION START` ブロックを
`logs/session.log` に追記します。

### `security-gate.sh`

`security-gate.sh` は `preToolUse` ゲートです。標準入力から JSON を読み取り、
`jq` で `.toolName` と `.toolArgs` を抽出します。

`bash` では、次の破壊的なパターンに一致するコマンドを拒否します。

- `rm -rf /`
- `rm -rf .`
- `DROP TABLE`
- `DROP DATABASE`
- `format `
- `mkfs.`
- `:(){` を含む fork bomb 構文

また、資格情報やシークレットに関する次のパスや語句を参照する bash コマンドも
拒否します。

- `.env`
- `credentials`
- `secrets`
- `.pem`
- `.key`
- `password`

`edit` と `create` では、`.toolArgs.path` を抽出します。フックの許可リスト式
（`src/`、`tests/`、`docs/`、`.github/`）に一致しないパスは拒否されます。
ただし、**リポジトリ相対**パスに対して照合される、トップレベルのプロジェクトファイル
（`README.md`、`AGENTS.md`、`mkdocs.yml`）の短い許可リストは例外です。
リポジトリルートを基準にすることで、ファイル名だけが一致する `/etc/README.md` が
すり抜けるのを防ぎます。`SECURITY.md` とライセンスファイルは許可リストの対象外であり、
これは [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md)
の「許可なく変更しない」というルールに沿っています。

許可された操作は次を出力します。

```json
{"permissionDecision":"allow"}
```

拒否された操作は `logs/security-denials.log` に 1 行追記し、次の形式を出力します。

```json
{"permissionDecision":"deny","permissionDecisionReason":"Access to credential/secret files blocked by security policy"}
```

### `audit-logger.sh`

`audit-logger.sh` は `postToolUse` フックです。`.toolName`、`.toolArgs`、
`.timestamp`、`.cwd` を読み取り、文字列化したツール引数を 500 文字に切り詰め、
操作を分類し、`logs/` を作成して、`logs/agent-audit.jsonl` に 1 行につき
1 つの JSON オブジェクトを追記します。

カテゴリは次のとおりです。

| ツール名 | カテゴリ |
|---|---|
| `bash` | `command-execution` |
| `edit` | `code-edit` |
| `create` | `file-creation` |
| `view` | `code-read` |
| `grep`, `glob` | `code-search` |
| その他 | `other` |

監査レコードの形式は次のとおりです。

```json
{
  "timestamp": "input timestamp",
  "logged_at": "UTC write time",
  "tool": "tool name",
  "category": "operation category",
  "args": "first 500 characters of toolArgs",
  "cwd": "working directory"
}
```

### `session-end.sh`

`session-end.sh` は標準入力から `.reason` を読み取り、
`logs/agent-audit.jsonl` と `logs/security-denials.log` が存在する場合は
それぞれの行数を数えた後、装飾付きの `SESSION END` ブロックを
`logs/session.log` に追記します。

## 修正済み: `preToolUse` が一度も実行されていなかった

以前の `retail-governance.json` では、`preToolUse` がディスク上に存在しない
`./.github/hooks/scripts/security-gate-notworking.sh` を参照していました。
実際のスクリプトは `security-gate.sh` であったため、エラーが表面化しないままゲートは一度も
実行されていませんでした。この問題は修正済みです。

ここから得られる教訓は、フックの構成ミスではエラーが表面化しないことがあるという点です。
特にセキュリティ制御を適用する拒否パスについては、ゲートが実際に発火することを
必ず確認してください。

## フックの手動テスト

リポジトリルートから、代表的なフック JSON をパイプで渡してスクリプトを直接
実行します。

```bash
echo '{"toolName":"bash","toolArgs":{"command":"cat .env"}}' | \
  ./.github/hooks/scripts/security-gate.sh
```

想定される結果は、拒否を示す JSON オブジェクトと、
`logs/security-denials.log` に追加された新しい 1 行です。

許可されるパスも同じ方法でテストできます。

```bash
echo '{"toolName":"create","toolArgs":{"path":"docs/example.md"}}' | \
  ./.github/hooks/scripts/security-gate.sh
```

## フックの一時的な無効化

短時間のローカル実験では、`.github/hooks/retail-governance.json` から該当する
イベントエントリを削除するか、そのイベントの配列を `[]` に設定し、コミット前に
元に戻します。無効化する範囲は可能な限り小さくしてください。たとえば、
セキュリティゲートの構成をテストする場合は `preToolUse` だけを空にします。

## 関連情報

- [アーキテクチャ](./architecture.md)
- [トラブルシューティング](./troubleshooting.md)
- [ガバナンス構成](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/hooks/retail-governance.json)
- [フックスクリプト](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/.github/hooks/scripts)
- [リポジトリエージェントのガイドライン](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md)
