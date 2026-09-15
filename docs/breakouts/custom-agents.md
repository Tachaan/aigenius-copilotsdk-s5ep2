# カスタムエージェント

このページでは、`.github/agents/` にあるリポジトリスコープのカスタムエージェントを
説明します。各エージェントは、YAML フロントマターと、レビュー、セキュリティ、
アクセシビリティ、PR の要約に特化するよう Copilot を設定する指示を含む
`.agent.md` ファイルです。

## `.agent.md` の形式

カスタムエージェントは、先頭にフロントマターを持つ Markdown ファイルを使用します。

```yaml
---
name: dotnet-reviewer
description: Senior .NET code reviewer specializing in C# best practices, security, and performance
tools: ['agent', 'read', 'search']
model: claude-sonnet-4.6
---
```

`name` はハンドル、`description` はそのエージェントが役立つ場面を Copilot に伝える
説明、`tools` はエージェントが利用できる機能を宣言する項目です。`model` がある場合は、
使用するモデルを固定します。Markdown 本文には、役割、レビューのチェックリスト、
出力形式、別エージェントによる検証の指示が含まれます。

## `dotnet-reviewer`

- **パス**: `.github/agents/dotnet-reviewer.agent.md`
- **フロントマターの name**: `dotnet-reviewer`
- **フロントマターの description**: `Senior .NET code reviewer specializing in C# best practices, security, and performance`
- **ツール**: `['agent', 'read', 'search']`
- **固定モデル**: `claude-sonnet-4.6`
- **トリガー**: 変更に .NET 固有のレビューが必要な場合、特にセキュリティ、
  パフォーマンス、null 許容参照型、非同期処理、破棄、EF Core のパターンを
  確認するときに使用します。
- **呼び出し例**:

  ```text
  @dotnet-reviewer review the changes in AgentHQDemo.Api for async and EF Core issues
  ```

このエージェントは、自身のレビュー後に `security-scanner` をサブエージェントとして
実行し、両方の検出結果を直接報告するようにも指示されています。

## `security-scanner`

- **パス**: `.github/agents/security-scanner.agent.md`
- **フロントマターの name**: `security-scanner`
- **フロントマターの description**: `Security-focused code reviewer that identifies vulnerabilities and compliance issues`
- **ツール**: `['agent', 'read', 'search']`
- **固定モデル**: `gpt-5.3-codex`
- **トリガー**: OWASP Top 10 の問題、入力検証、認証と認可、機密データの露出、
  安全でないパース処理、ログ記録の不足をレビューするときに使用します。
- **呼び出し例**:

  ```text
  @security-scanner check the chat and transaction endpoints for OWASP issues
  ```

このエージェントは、各検出結果に重大度、該当する場合は CWE、場所、攻撃シナリオ、
修復方法、参照情報を含めるよう求めます。UI コードがある場合は、
`accessibility-auditor` をサブエージェントとして実行するよう指示されています。

## `pr-summary`

- **パス**: `.github/agents/pr-summary.agent.md`
- **フロントマターの name**: `pr-summary`
- **フロントマターの description**: `Generates concise, informative PR summaries from code changes`
- **ツール**: `['agent', 'read', 'search']`
- **固定モデル**: 宣言なし。
- **トリガー**: pull request の説明を準備するとき、差分を要約するとき、または変更を
  機能、修正、テスト、ドキュメント、構成ごとに分類するときに使用します。
- **呼び出し例**:

  ```text
  @pr-summary summarise this PR and call out reviewer risks
  ```

想定される出力には、1 行の要約、分類された変更の概要、変更された主要ファイル、
影響評価、テストに関する注記が含まれます。また、`dotnet-reviewer` という
別エージェントによる検証を
求め、最終的なコード品質セクションには Critical と High の検出結果だけを含めます。

## `accessibility-auditor`

- **パス**: `.github/agents/accessibility-auditor.agent.md`
- **フロントマターの name**: `accessibility-auditor`
- **フロントマターの description**:
  "Use this agent when the user asks to review code for accessibility issues or
  compliance.

  Trigger phrases include:
  - 'check this code for accessibility issues'
  - 'review for WCAG compliance'
  - 'audit for accessibility problems'
  - 'find accessibility violations'
  - 'is this accessible?'

  Examples:
  - User says 'can you review this component for accessibility?' → invoke this
  agent to audit the code
  - User asks 'does this form meet WCAG standards?' → invoke this agent to
  check compliance
  - User says 'what accessibility issues might this have?' → invoke this agent
  to identify problems
  - After writing UI code, proactively invoke if accessibility concerns might
  exist"
- **ツール**: `['read', 'search']`
- **固定モデル**: 宣言なし。
- **トリガー**: description には "check this code for accessibility issues"、
  "review for WCAG compliance"、"audit for accessibility problems"、
  "find accessibility violations"、"is this accessible?" などの語句が
  明示されています。
- **呼び出し例**:

  ```text
  @accessibility-auditor review the Blazor components for WCAG 2.1 AA issues
  ```

このエージェントは、セマンティック HTML、ARIA、キーボードナビゲーション、
色のコントラスト、フォーカス状態、フォームラベル、モーション、メディアの代替手段、
レスポンシブ動作を確認します。

## 共通指示とレビュー固有の指示

`.github/copilot-instructions.md` は、このリポジトリ内のすべてのアシスタントに
適用される共通標準です。.NET 10 小売分析アプリ、コーディング規約、Copilot SDK の
パターン、テスト要件、セキュリティルールについて説明しています。

`.github/copilot-review-instructions.md` は、より限定的な指示です。レビュー時の
コンテキストとして、GitHub Copilot SDK v1.0.9 の名前空間 `GitHub.Copilot`、
明示的な `session.On<T>(...)` の使用、SSE ストリーミングのルール、モデル検出の
想定動作、明示的に依頼されない限りレビューで指摘すべきでない意図的なデモ用
コードスメルを示します。

## モデル固定から得られた教訓

`security-scanner.agent.md` は現在 `model: gpt-5.3-codex` に固定されています。
元の値は大文字と小文字が誤っており、末尾に空白もありました。実際のモデル一覧に
存在するのは `gpt-5.3-codex` だけです。無効なモデル指定はエージェントの起動を
妨げる可能性があるため、フロントマターのモデル ID は正確に記述してください。

## 関連情報

- [アーキテクチャ](./architecture.md)
- [フックとガバナンス](./hooks-and-governance.md)
- [スキル](./skills.md)
- [Copilot の共通指示](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-instructions.md)
- [レビュー指示](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-review-instructions.md)
- [エージェントフォルダー](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/.github/agents)
