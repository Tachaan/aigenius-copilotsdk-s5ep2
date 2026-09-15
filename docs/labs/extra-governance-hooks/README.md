# 追加ラボ — ガバナンスフック

> **📎 追加ラボ — Copilot SDK の内容ではありません。**
> ここでは **Copilot CLI** の機能である、`.github/hooks/` で駆動するシェルフックを扱います。
> SDK には独自のインプロセス版があります。[ラボ 03 — ツール](../03-tools/) の権限に関する
> セクションを参照してください。オプションであり、番号付きの SDK 学習手順からは独立しています。

**目標:** `preToolUse` セキュリティゲートでシークレットファイルへのアクセスを実際にブロックし、
監査ロガーがアクティビティを記録する様子を確認して、誤設定されたまま気付かれないフックが
フックなしよりも危険な理由を学びます。

**所要時間:** 約 20 分

**前提条件:** [Extra — カスタムエージェント](../extra-custom-agents/) を完了していること。
フックスクリプトが依存する `jq` がインストールされていること。

## 手順 1 — フックの接続方法を確認する

```bash
cat .github/hooks/retail-governance.json
ls -l .github/hooks/scripts/
```

4 つのライフサイクルイベントが、それぞれスクリプトに対応付けられています。

| イベント | スクリプト | 目的 |
|:------|:-------|:--------|
| `sessionStart` | `session-init.sh` | ポリシーを通知し、監査証跡を開始する |
| `preToolUse` | `security-gate.sh` | ツール呼び出しの実行前に**許可または拒否**する |
| `postToolUse` | `audit-logger.sh` | 実際に起きたことを記録する |
| `sessionEnd` | `session-end.sh` | セッションを終了して要約する |

各エントリでは、`type`、実行する `bash` スクリプト、作業ディレクトリ、`timeoutSec` を宣言します。

何かを*停止*できるのは `preToolUse` だけです。他のイベントは監視のみを行います。

## 手順 2 — 注意すべき事例

このリポジトリは一時期、壊れたゲートを含んだ状態で公開されていました。構成の参照先は
次のとおりでした。

```
./.github/hooks/scripts/security-gate-notworking.sh
```

しかし、ディスク上のファイルは `security-gate.sh` でした。参照されたスクリプトは
**存在しませんでした**。

ゲートはエラーも警告も出さず、単に一度も実行されませんでした。リポジトリは完全に統制されて
いるように見える一方、すべてのツール呼び出しが未検査で通過しました。以前の `.env` には
「preToolUse フックがこのファイルへのアクセスを BLOCK するはず」とまでコメントされて
いましたが、実際にはブロックされませんでした。

現在は修正されています。ここに、このラボで最も重要な教訓があります。

> ⚠️ **誤設定されたまま気付かれない制御は、制御がない状態よりも危険です。**
> 誤った安心感を生み出すためです。ゲートが実際に作動することを必ず確認してください。

参照が現在は正しいことを確認します。

```bash
grep -o '"bash": "[^"]*"' .github/hooks/retail-governance.json
```

一覧にあるすべてのパスが `.github/hooks/scripts/` に存在する必要があります。

## 手順 3 — ゲートを確認する

```bash
cat .github/hooks/scripts/security-gate.sh
```

規約は単純です。stdin から JSON を受け取り、stdout へ判定を出力します。

```bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs')
```

次の 3 つの場合に拒否します。

1. **破壊的な bash** — `rm -rf /`、`rm -rf .`、`DROP TABLE`、
  `DROP DATABASE`、`format `、`mkfs.`、fork bomb パターン
2. **シークレットへのアクセス** — `.env`、`credentials`、`secrets`、`.pem`、`.key`、
  `password` に言及するコマンド
3. **範囲外への書き込み** — `src/`、`tests/`、`docs/`、`.github/` の外部に対する
  `edit`/`create`

そして、次のいずれかを出力します。

```json
{"permissionDecision":"allow"}
{"permissionDecision":"deny","permissionDecisionReason":"..."}
```

⚠️ 拒否する場合でも終了コードは `0` です。*判定*は終了コードではなく JSON ペイロードで
伝達されます。0 以外で終了すると、意図的な拒否ではなく壊れたフックに見えてしまいます。

## 手順 4 — ゲートがシークレットをブロックすることを確認する

スクリプトが実行可能で、ログディレクトリが存在することを確認します。

```bash
chmod +x .github/hooks/scripts/*.sh
mkdir -p logs
```

実際のツール呼び出しが送信する JSON をパイプし、直接テストします。

```bash
echo '{"toolName":"bash","toolArgs":{"command":"cat .env"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

想定される出力:

```json
{"permissionDecision":"deny","permissionDecisionReason":"Access to credential/secret files blocked by security policy"}
```

これでゲートが動作していることを確認できます。以前はこのチェック自体が実行されていませんでした。

## 手順 5 — 他の経路をテストする

破壊的なコマンド:

```bash
echo '{"toolName":"bash","toolArgs":{"command":"rm -rf /"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `"Destructive command blocked by retail governance policy"`

許可されたディレクトリの外部への書き込み:

```bash
echo '{"toolName":"create","toolArgs":{"path":"/etc/hosts"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `"File edits restricted to src/, tests/, docs/, .github/, and top-level project docs"`

許可される必要があるトップレベルのプロジェクトファイル:

```bash
echo '{"toolName": "create", "toolArgs": {"path": "README.md"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `{"permissionDecision":"allow"}`

許可リストは**リポジトリ相対**パスに対して照合されるため、リポジトリ外にある同名のファイルは
引き続き拒否されます。

```bash
echo '{"toolName": "create", "toolArgs": {"path": "/etc/README.md"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ 拒否されます。ファイル名だけで照合していた場合は通過してしまいます。

そして、通過する必要がある正当な呼び出し:

```bash
echo '{"toolName":"bash","toolArgs":{"command":"dotnet build"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `{"permissionDecision":"allow"}`

⚠️ **許可されるケースも必ずテストしてください。** すべてを拒否するゲートは、「ブロックしたか」
というテストにはすべて合格しますが、リポジトリを使用不能にします。

## 手順 6 — 拒否ログを確認する

```bash
cat logs/security-denials.log
```

各拒否について、UTC タイムスタンプ、ツール、理由が追記されます。

```
2026-08-10T11:04:35Z DENIED tool=bash reason="Access to credential/secret files blocked by security policy"
```

これはコンプライアンスレビュアーが求める成果物です。制御が存在する証拠と、実際に作動した
証拠の両方になります。

## 手順 7 — ゲートの動作にファイルの存在は不要

このリポジトリにはシークレットファイルをコミットしません。`.env` は gitignore の対象であり、
決してチェックインしてはいけません。それでもゲートの効果は変わりません。ディスク上の
ファイルではなく、**コマンドテキスト**を照合するためです。

`.env` がないことを確認してから、それでも読み取りを試みます。

```bash
ls .env 2>/dev/null || echo "no .env present"
echo '{"toolName":"bash","toolArgs":{"command":"cat .env"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

引き続き拒否されます。他のシークレットパターンでも同様です。

```bash
echo '{"toolName":"bash","toolArgs":{"command":"cat ~/.ssh/id_rsa.key"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

💡 これには一長一短があります。テキスト照合のため、まだ存在しないファイルを利用してゲートを
回避することはできません。一方で、トリガー語を避けるコマンド（`cat .en''v` やスクリプト経由の
読み取り）では回避できます。意図的な攻撃者への防御ではなく、ミスを防ぐガードレールとして
扱ってください。

## 手順 8 — フックを有効にしてセッションを実行する

```bash
copilot -p "List the files in the src directory" --allow-all-tools
```

次に、監査ロガーが記録した内容を確認します。

```bash
ls -la logs/
tail -20 logs/*.jsonl 2>/dev/null || tail -20 logs/*.log 2>/dev/null
```

💡 フックは CLI によってセッションごとに構成されます。何も表示されない場合は、CLI がこの
リポジトリの `.github/hooks/retail-governance.json` を読み込んでいることを確認してください。

## 手順 9 — フックを無効化する

フックの開発中は無効にしたい場合があります。構成ファイルの名前を変更するか、

```bash
mv .github/hooks/retail-governance.json .github/hooks/retail-governance.json.off
# restore with the reverse
```

個別イベントの配列エントリを削除してコメントアウトします。

⚠️ 共有ブランチでゲートを無効にしたまま、復元を忘れないでください。手順 2 とまったく同じ、
気付かれない障害を再現してしまいます。構成内のすべての `bash` パスがディスク上に存在する
ことを検証する CI チェックの追加を検討してください。

## ✅ チェックポイント

- [x] 4 つのフックイベントと、拒否できるイベントを説明できる
- [x] ゲートがシークレット、破壊的なコマンド、範囲外への書き込みをブロックすることを確認した
- [x] 正当な呼び出しが引き続き通過することを確認した
- [x] 拒否ログの証拠を確認した
- [x] 壊れた参照が危険だった理由を説明できる

## 💡 発展課題

`main` に対する `git push --force` をブロックするルールを `security-gate.sh` に追加します。
force push が拒否されることと、通常の `git push` が引き続き通過することの両方をテストします。

## 関連項目

- 次へ: [Extra — API の拡張](../extra-extend-api/)
- [補足資料: フックとガバナンス](../../breakouts/hooks-and-governance.md)
- [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md) — AI エージェント向けのリポジトリルール
