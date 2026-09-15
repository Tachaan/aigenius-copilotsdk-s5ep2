# Blazor フロントエンド

このウォークスルーでは、小売分析 API のフロントエンドとなる Blazor WebAssembly クライアントについて説明します。API への接続、チャット応答のメッセージ一覧へのストリーミング、ローカル設定の永続化、モデルピッカーと現在のモデル一覧の同期方法を確認します。

## アプリの構成とポート

フロントエンドは、次の場所にある Blazor WebAssembly アプリです。
[`AgentHQDemo.Web`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/AgentHQDemo.Web)

このリポジトリでは、起動プロファイルを上書きする明示的な `--urls` を指定して2つのサービスを起動します。

```bash
dotnet run --project src/AgentOrchestrator/AgentHQDemo.Web --urls "http://localhost:5051"
```

このため、ドキュメント、図、ラボでは一貫して UI に **5051**、API に **5050** を使用します。⚠️ リポジトリに含まれる起動プロファイルの既定値は*別の*ポートで、Web プロジェクトは 5240、API は 5167 です。そのため、`--urls` なしで実行する場合（または IDE で F5 を押す場合）は、それらのポートで提供され、UI の既定の API ベースアドレス `http://localhost:5050` と一致しなくなります。ドキュメントどおりに `--urls` を渡すか、一致するように `ApiBaseUrl` を設定してください。

[`AgentHQDemo.Web/Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Program.cs)
では、API のベースアドレスを構成します。

```csharp
var apiBase = builder.Configuration["ApiBaseUrl"] ?? "http://localhost:5050";
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(apiBase) });
```

API は
[`AgentHQDemo.Api/Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs)
で、任意のオリジン、メソッド、ヘッダーを許可する既定のポリシーを使って CORS を有効にします。これにより、ローカル開発 URL で提供される WebAssembly アプリは、デモ中に構成済みの API ベースアドレスを呼び出せます。

## `Home.razor`

[`Home.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Pages/Home.razor) は
メインのチャットページです。次のページ状態を管理します。

- `Messages`: 順序を保持したチャット履歴。
- `SelectedModel`: 現在選択されている Copilot モデル。
- `Models`: モデル ID と表示名を対応付けるディクショナリ。
- `IsDarkTheme`: 現在のテーマを示すフラグ。
- `IsStreaming`: アシスタントの応答が進行中かどうか。

メッセージがない場合、ページにはウェルカムパネルと `SuggestionChips` が表示されます。メッセージが存在する場合は、それぞれを `Message` コンポーネントでレンダリングします。

## ストリーミング状態とスクロール

`Home.razor.SendMessage` はユーザーのメッセージを追加して保存し、その後に空のアシスタント用プレースホルダーを追加します。`IsStreaming` が true の間は入力を無効にし、`ChatService.StreamChatAsync` からチャンクが到着するたびにアシスタントのメッセージを更新します。

ページはトークンごとにレンダリングする代わりに、`Timer` を使っておよそ毎秒20フレームで UI 更新をまとめます。レンダリング後は JavaScript ヘルパーを呼び出し、メッセージコンテナーを一番下までスクロールして、コードブロックを強調表示します。

## ローカルストレージへの永続化

[`StorageService`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/StorageService.cs)
は `Blazored.LocalStorage` をラップします。次の3つのローカル値を保存します。

| キー | 用途 |
| --- | --- |
| `chat_messages` | 永続化された `ChatMessage` の履歴。 |
| `selected_model` | 次回のページ読み込み時に復元するモデル。 |
| `theme` | 保存された `dark` または `light` テーマ。 |

`Home.razor.OnInitializedAsync` は、モデル一覧を取得する前に3つの値をすべて読み込みます。

## モデルピッカー

[`Header.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Components/Header.razor)
はモデルピッカーをレンダリングします。現在の `Models` ディクショナリを受け取り、選択したオプションを `SelectedModel` にバインドします。

```razor
<select id="model-select" @bind="SelectedModel" @bind:after="OnModelChanged">
```

ユーザーが選択を変更すると、`Header.OnModelChanged` が `SelectedModelChanged` コールバックを呼び出します。`Home.razor.OnModelChanged` はローカル状態を更新し、`StorageService.SetSelectedModelAsync` を通じて新しいモデルを保存します。

## 現在のモデル一覧の取得

[`ChatService.GetModelsAsync`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/ChatService.cs)
は API からモデルのメタデータを読み込みます。

```csharp
var models = await _http.GetFromJsonAsync<List<ApiModel>>("/api/chat/models");
```

API が1つ以上のモデルを返すと、サービスはそれを `Header.razor` が使用する `Dictionary<string, string>` に変換します。API に到達できない場合や利用できないデータが返された場合は、オフライン時の回復性のために用意された静的カタログ `ChatService.AvailableModels` にフォールバックします。

## 保存済みモデルの陳腐化への対処

ローカルストレージに保存されたモデルが、サインイン中のアカウントでは利用できなくなることがあります。`Home.razor.OnInitializedAsync` は、現在のモデル一覧を取得した後にこの状況を処理します。

```csharp
if (!Models.ContainsKey(SelectedModel))
{
    SelectedModel = Models.ContainsKey("claude-haiku-4.5")
        ? "claude-haiku-4.5"
        : Models.Keys.First();
}
```

その後、ページは代替モデルを永続化します。これにより、古い localStorage の値が原因で、API では提供されなくなったモデルをチャットリクエストが使用する事態を防ぎます。

## 補助コンポーネント

[`ChatInput`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Components/ChatInput.razor)
はテキストエリアと送信ボタンを提供します。ボタンのクリックまたは Shift なしの Enter で送信し、読み込み中は入力を無効にし、空白だけのメッセージを除外し、初回レンダリング後に入力へフォーカスします。

[`Message`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Components/Message.razor)
はユーザーとアシスタントのメッセージをレンダリングします。アシスタントのコンテンツが空の場合は入力中インジケーターを表示し、空でない場合は Markdig を使用して Markdown からレンダリングします。コードブロックには JavaScript による強調表示用のマークを付けます。

[`SuggestionChips`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Components/SuggestionChips.razor)
は、定義済みの小売分析プロンプトを表示します。チップを選択すると、入力したメッセージと同じ `Home.razor.SendMessage` 経路でそのプロンプトを送信します。

## 関連情報

- [Copilot SDK の組み込み](./01-copilot-sdk-integration.md)
- [SSE による応答のストリーミング](./02-sse-streaming.md)
- [小売ドメイン](./03-retail-analytics.md)
- ソース:
  [`Home.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Pages/Home.razor),
  [`Header.razor`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Components/Header.razor),
  [`ChatService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/ChatService.cs),
  [`StorageService.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Services/StorageService.cs),
  [`AgentHQDemo.Web/Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Web/Program.cs),
  [`AgentHQDemo.Api/Program.cs`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator/AgentHQDemo.Api/Program.cs),
  [`Components`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/tree/main/src/AgentOrchestrator/AgentHQDemo.Web/Components)
