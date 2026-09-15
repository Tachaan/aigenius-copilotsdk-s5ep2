# トラブルシューティング

このページは、Agent HQ デモで発生する問題、その原因、修正方法をまとめた実践的な
リファレンスです。一般的な .NET や GitHub Actions の動作ではなく、リポジトリ内の
ファイルから確認できる問題に焦点を当てています。

## `MSB3923: failed to download Copilot CLI`

**原因**: `GitHub.Copilot.SDK` はビルド時に、対応する Copilot CLI バイナリを
`registry.npmjs.org` からダウンロードします。企業プロキシやオフラインの
開発マシンによって、このダウンロードがブロックされることがあります。

**修正方法**: CLI をグローバルにインストールし、`Directory.Build.props` に
自動検出させます。

```bash
npm install -g @github/copilot
dotnet build src/AgentOrchestrator/AgentHQDemo.slnx
```

必要に応じて、明示的にオーバーライドします。

```bash
dotnet build src/AgentOrchestrator/AgentHQDemo.slnx \
  -p:CopilotCliBinaryPath=/path/to/copilot
```

ローカル検出を無効にし、SDK の通常のダウンロード動作に戻すには、次を実行します。

```bash
dotnet build src/AgentOrchestrator/AgentHQDemo.slnx \
  -p:CopilotUseLocalCli=false
```

## CodeQL Analysis に `skipped` と表示される

**原因**: プライベートリポジトリでは想定される動作です。リポジトリがパブリックでない
場合、コードスキャン結果のアップロードには GitHub Advanced Security が必要です。

**修正方法**: スキップされたジョブはリポジトリの障害ではなく、意図された動作として
扱います。ワークフローには次の条件が設定されています。

```yaml
if: github.event.repository.visibility == 'public' || vars.ENABLE_CODEQL == 'true'
```

対象の組織に必要なコードスキャンの利用資格がある場合にのみ、リポジトリ変数
`ENABLE_CODEQL=true` を設定してください。

## `Model ... is not available`

**原因**: サインイン中の Copilot アカウントではそのモデル ID を使用できないか、
ID が古くなっています。

**修正方法**: 新しいコードにモデル ID をハードコードしないでください。アプリは
`/api/chat/models` から最新の一覧を取得します。このエンドポイントは
`CopilotChatService.ListModelsAsync` を呼び出し、CLI に接続できない場合にのみ
小規模な静的カタログへフォールバックします。

## JSON-RPC または `PingResponse` の逆シリアル化エラー

**原因**: Copilot SDK と Copilot CLI のバージョンが一致しないと、JSON-RPC の
逆シリアル化に失敗することがあります。

**修正方法**: `GitHub.Copilot.SDK` のアップグレードと Copilot CLI の更新を同時に
行います。このリポジトリでは SDK v1.0.9 を使用しています。また、v1.0.0 の
API 変更も確認してください。

- 名前空間が `GitHub.Copilot.SDK` から `GitHub.Copilot` に移動しました
- `session.On<T>(...)` には明示的な型引数が必要になりました

## Port already in use: 5050 or 5051

**原因**: 別のプロセスが API のポート 5050 または Blazor のポート 5051 にすでに
バインドされています。以前の実行から残っているサーバーによって、気づかないまま
古いコードが配信されることがあります。

**修正方法**: プロセスを特定して停止します。

```bash
lsof -ti:5050
lsof -ti:5051
```

次に、返されたプロセス ID を停止し、該当するアプリを再起動します。

```bash
kill 12345  # replace 12345 with the process id returned by lsof
dotnet run --project src/AgentOrchestrator/AgentHQDemo.Api --urls "http://localhost:5050"
dotnet run --project src/AgentOrchestrator/AgentHQDemo.Web --urls "http://localhost:5051"
```

## Blazor UI に古いモデルまたは無効なモデルが表示される

**原因**: 選択したモデルは Web アプリのブラウザー localStorage に保存されます。
モデルが利用できなくなった後も、その値が残ることがあります。

**修正方法**: 選択したモデルが実行時のモデル一覧に存在しなくなると、アプリは
`Home.razor` で保存値をリセットします。それでも UI が古い状態に見える場合は、
`localhost:5051` のサイトデータを消去してください。

## `GitHub Actions hosted runners are disabled`

**原因**: 組織またはエンタープライズのポリシーでホステッドランナーが無効に
なっています。これはリポジトリのビルドやワークフロー構文の問題ではありません。

**修正方法**: 組織またはエンタープライズの管理者に、ホステッドランナーを有効にするか、
このリポジトリで承認済みのランナーを用意するよう依頼してください。

## ビルドは成功するが、テストがソリューションを見つけられない

**原因**: ソリューションはリポジトリルートにありません。
`src/AgentOrchestrator/AgentHQDemo.slnx` にあります。

**修正方法**: ソリューションのパスを明示的に渡します。

```bash
dotnet restore src/AgentOrchestrator/AgentHQDemo.slnx
dotnet build src/AgentOrchestrator/AgentHQDemo.slnx
dotnet test src/AgentOrchestrator/AgentHQDemo.slnx
```

`.github/workflows/ci.yml` でも、復元、ビルド、テストにこのパスを使用しています。

## 関連情報

- [アーキテクチャ](./architecture.md)
- [フックとガバナンス](./hooks-and-governance.md)
- [`Directory.Build.props`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/Directory.Build.props)
- [CI ワークフロー](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/workflows/ci.yml)
- [CodeQL ワークフロー](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/workflows/codeql.yml)
- [レビュー指示](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/copilot-review-instructions.md)
