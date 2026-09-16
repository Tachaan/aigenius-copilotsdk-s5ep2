# ブレイクアウト

.NET と Python の両方で使える共通資料です。リファレンスページと、
2 つの Copilot CLI ラボを収録しています。

## リファレンス

| ドキュメント | 用途 |
|:----|:------------|
| [アーキテクチャ](architecture.md) | システム図、リクエストのシーケンス、またはデータモデルを確認したいとき |
| [システムマップ](../system-map/) | アーキテクチャを対話的に探索したいとき |
| [カスタムエージェント](custom-agents.md) | `.agent.md` を作成または呼び出すとき |
| [フックとガバナンス](hooks-and-governance.md) | `preToolUse` ゲートを設定したり、監査証跡を確認したりするとき |
| [スキル](skills.md) | 5 つのスキルの機能と Copilot がそれらを選ぶタイミングを知りたいとき |
| [トラブルシューティング](troubleshooting.md) | **問題が発生したとき**。まずここを確認してください |

## 追加ハンズオン

SDK ではなく **Copilot CLI** を扱う任意のラボです。言語に依存しないため、
各トラック内ではなくここに配置されています。[.NET](../labs/) と
[Python](../labs-python/) のどちらのパスからでも実施できます。

| ラボ | 内容 | 所要時間 |
|:----|:-------|:-----|
| [カスタムエージェント](../labs/extra-custom-agents/) | `.agent.md` ファイル、意図的なコードスメルのエージェント支援レビュー | 約 20 分 |
| [ガバナンスフック](../labs/extra-governance-hooks/) | シェルフック、セキュリティゲート、監査ログ | 約 20 分 |

フック形式の制御に相当する SDK の機能はツール定義です。
[.NET ラボ 03](../labs/03-tools/) または [Python ラボ 03](../labs-python/03-tools/)
を参照してください。

## よくある問題の早見表

| 症状 | 参照先 |
|:--------|:----|
| `MSB3923` — can't download the Copilot CLI | [トラブルシューティング](troubleshooting.md) |
| CodeQL ジョブに "skipped" と表示される | [トラブルシューティング](troubleshooting.md) — プライベートリポジトリでは想定どおりです |
| `Model "..." is not available` | [トラブルシューティング](troubleshooting.md) |
| ポート 5050/5051 がすでに使用されている | [トラブルシューティング](troubleshooting.md) |
| `MSB1003` — no project or solution found | ソリューションは `src/AgentOrchestrator/AgentHQDemo.slnx` にあります |
| フックが実行されていないように見える | [フックとガバナンス](hooks-and-governance.md) |

## 関連情報

- [.NET ラボ](../labs/) · [.NET デモ](../demos/)
- [Python ラボ](../labs-python/) · [Python デモ](../demos-python/)
- [ルート README](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/README.md) — クイックスタートとエンドポイントのリファレンス
- [`AGENTS.md`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/AGENTS.md) — AI エージェント向けのリポジトリルール
