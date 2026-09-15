# スキル

このページでは、`.github/skills/` 以下にある 5 つのリポジトリスキルについて
説明します。スキルは再利用可能な知識パックであり、依頼が特定のドメイン、規約、
または検証ワークフローに一致すると Copilot が呼び出すことができます。

## フォルダー規約

各スキルは次の場所にあります。

```text
.github/skills/<skill-name>/SKILL.md
```

`SKILL.md` は、少なくとも `name` と `description` を含むフロントマターで始まります。
一部のスキルは `license` や `model` も宣言します。本文には、ドメインルール、例、
チェックリスト、出力形式が記載されています。

## スキル、エージェント、指示ファイルの違い

- **スキル**は、トピック別のリファレンスです。フロントエンド生成や ML モデルの
  レビューなど、特定の種類の作業を処理する方法を Copilot に教えます。
- `.github/agents/` の**エージェント**は、独自のツール、プロンプト、場合によっては
  固定モデルを持つ、名前付きのペルソナです。
- `.github/copilot-instructions.md` や `.github/copilot-review-instructions.md`
  などの**指示ファイル**は、多くのタスクに適用される広範なリポジトリコンテキストです。

## `brand-guidelines`

- **パス**: `.github/skills/brand-guidelines/SKILL.md`
- **フロントマターの name**: `brand-guidelines`
- **フロントマターの description**:
  "Guides AI agents when generating branded aviation and loyalty program
  websites. Use this skill when building marketing pages, product catalogs,
  hero sections, loyalty points displays, or any customer-facing UI for airline
  and frequent flyer contexts. Provides a complete visual design system with
  colors, typography, spacing, components, and layout patterns."
- **その他のフロントマター**: `license: MIT`
- **対象範囲**: カラートークン、タイポグラフィ、余白、商品カード、ロイヤルティ
  ポイント表示、ナビゲーション、CTA ボタン、ヒーローセクション、フッター、
  ブランド準拠チェックリスト。
- **Copilot が呼び出す場面**: ブランド化されたマーケティングページ、商品カタログ、
  ロイヤルティポイント UI、ヒーローセクション、または顧客向けの航空会社／
  フリークエントフライヤー体験の構築やレビューを依頼されたとき。

## `data-pipeline-conventions`

- **パス**: `.github/skills/data-pipeline-conventions/SKILL.md`
- **フロントマターの name**: `data-pipeline-conventions`
- **フロントマターの description**:
  "Enforces data pipeline coding conventions for retail analytics. Use this
  skill when writing or reviewing ETL code, data ingestion, transformation
  logic, or data quality checks. Covers schema management, idempotency,
  validation, partitioning, and observability patterns for production data
  pipelines."
- **その他のフロントマター**: `license: MIT`
- **対象範囲**: 冪等な ETL、スキーマ管理、検証、デッドレター処理、パーティション分割、
  バッチ処理、可観測性、データ品質チェック、命名規則、パイプラインテスト。
- **Copilot が呼び出す場面**: 小売分析向けの ETL コード、データ取り込み、変換、
  スキーマ進化、検証、データ品質チェックを作成またはレビューするとき。

## `demo-verifier`

- **パス**: `.github/skills/demo-verifier/SKILL.md`
- **フロントマターの name**: `demo-verifier`
- **フロントマターの description**:
  "**CRITICAL: Use this skill to verify demo capabilities.** Reads the .NET and
  Python demo walkthroughs and cross-references every claimed capability
  against current GitHub documentation. Reports what is confirmed, in preview,
  or deprecated. MUST be invoked when reviewing demo accuracy, checking feature
  availability, or preparing for a live demo."
- **その他のフロントマター**: `license: MIT`
- **対象範囲**: デモの手順書の読み取り、記載された機能の抽出、現在の GitHub
  ドキュメントとの照合、機能が確認済み、プレビュー中、変更済み、利用不可の
  いずれであるかの報告。
- **Copilot が呼び出す場面**: ライブデモの前、デモドキュメントの更新後、
  デモの正確性を確認するとき、または機能の提供状況の検証を依頼されたとき。

## `frontend-conventions`

- **パス**: `.github/skills/frontend-conventions/SKILL.md`
- **フロントマターの name**: `frontend-conventions`
- **フロントマターの description**:
  "Guides AI agents when generating frontend websites from scratch. Use this
  skill when creating HTML pages, styling with CSS, adding JavaScript
  interactivity, or building static sites. Covers semantic HTML5, modern CSS
  patterns, accessibility, performance, and component patterns for
  production-ready frontends."
- **その他のフロントマター**: `license: MIT`、`model: gpt-5.4`
- **対象範囲**: セマンティック HTML5、ランドマーク、見出し階層、CSS カスタム
  プロパティ、Grid、Flexbox、レスポンシブタイポグラフィ、モバイルファーストの
  ブレークポイント、コンポーネントパターン、アクセシビリティ、パフォーマンス、
  JavaScript パターン、フロントエンドレビューのチェックリスト。
- **Copilot が呼び出す場面**: Web サイト、ランディングページ、静的フロントエンド、
  HTML/CSS/JavaScript ページの構築を依頼されたとき、またはフロントエンドコードの
  アクセシビリティやパフォーマンスをレビューするとき。

## `ml-model-review`

- **パス**: `.github/skills/ml-model-review/SKILL.md`
- **フロントマターの name**: `ml-model-review`
- **フロントマターの description**:
  "Reviews ML model code for correctness, fairness, and production readiness.
  Use this skill when writing or reviewing customer segmentation, prediction
  models, feature engineering, or model evaluation code. Checks for data
  leakage, bias, reproducibility, and deployment risks in retail analytics ML
  pipelines."
- **その他のフロントマター**: `license: MIT`
- **対象範囲**: データリーク、特徴量エンジニアリング、設定可能なしきい値、評価指標、
  バイアスと公平性のチェック、再現性、本番対応、ドリフト監視、ML レビューの
  チェックリスト。
- **Copilot が呼び出す場面**: 顧客セグメンテーション、予測モデル、特徴量
  エンジニアリング、モデル評価、小売分析 ML パイプラインのコードを作成または
  レビューするとき。

## 関連情報

- [カスタムエージェント](./custom-agents.md)
- [アーキテクチャ](./architecture.md)
- [スキルフォルダー](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/.github/skills)
- [Copilot の共通指示](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-instructions.md)
- [デモ資料](../demos/)
