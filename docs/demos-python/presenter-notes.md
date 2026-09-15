# Python デモ発表カンペ

## このデモの着地点

**「既存の業務アプリに、データを参照して回答する Agent を組み込める。その接続点と権限はアプリ側で設計する」**を持ち帰ってもらいます。

前段で説明済みの「通常の Copilot と Agent の違い」「SDK の構成要素」「組み込み先・実行・認証・隔離方式」は説明し直しません。実際のアプリとコードで答え合わせをします。

想定は **デモ本編 40 分**。前段のスライド説明は含めず、操作・応答待ち・短い確認質問を含みます。「完成形」は今回のデモの完成形であり、本番要件をすべて満たすという意味ではありません。

**読み方:** 各項目の **操作** を進めながら、直下の **トーク** を話します。一項目は「質問を送る」「一つの処理を説明する」程度のまとまりです。キー操作そのものは読み上げません。結果確認は実際に確認できたときだけ、待機中のトークは応答が来るまで使います。「場合」と付いた項目は、その状況になったときだけ読みます。

### 投影する画面

次は投影前の準備用です。**本編の操作にも画面名と行き先を毎回書いているため、この一覧を覚える必要はありません。** ブラウザーのタブをこの順に並べると、併記したキーで移動できます。

**API の取得・ログ確認・ラボ・テストは VS Code 内で行います。** ブラウザーは利用者のチャット体験と図・資料の表示にだけ使います。以下の API コマンドは PowerShell 用です。

- **ブラウザーのチャット画面:** `http://localhost:5070/`。左から一番目のタブ（`Ctrl+1`）。
- **ブラウザーのシステムマップ:** ローカルの [システムマップ HTML](../system-map/map.html)。二番目のタブ（`Ctrl+2`）。
- **ブラウザーのガバナンス資料:** 公開できる[フックの説明文書](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/docs/breakouts/hooks-and-governance.md)。三番目のタブ（`Ctrl+3`）。組織の管理画面ではない。
- **VS Code のコード画面:** ローカルのソースを開くエディター。本文に開くファイルと行番号を記載する。
- **VS Code の API ログ用ターミナル:** uvicorn が動いているターミナルを `API` と改名しておく。ログ表示専用で、ラボコマンドは入力しない。
- **VS Code の実行用ターミナル:** 別の PowerShell を `LAB` と改名し、Python プロジェクトを作業場所にしておく。API の GET、ラボ、テストをここで一つずつ実行する。

### 40 分の流れ

- **0:00–1:00（1 分）:** スライドからチャット画面へ。
- **1:00–6:00（5 分）:** 完成形を見せ、回答を取引データと照合。
- **6:00–14:00（8 分）:** ストリーミングのコードとイベントラボ。
- **14:00–19:00（5 分）:** モデル選択の実行とコード。
- **19:00–28:00（9 分）:** 直接登録ツール、MCP、既存の業務処理。
- **28:00–32:00（4 分）:** システムマップで全体を整理。
- **32:00–34:00（2 分）:** 利用画面へ戻り、表示履歴を確認。
- **34:00–39:00（5 分）:** 権限、読み取り専用 DB、フック。
- **39:00–40:00（1 分）:** 最初の回答画面で締める。

**行番号について:** 2026-09-14 の作業ツリーが基準です。VS Code の `Ctrl+P` でファイルを開き、`Ctrl+G` で行に移動します。リンク先の GitHub と手元の内容が異なる場合は手元を優先し、行がずれたら併記した関数名で検索します。コードの編集や機能追加は本編で行いません。

**進行の目安:** 14 分でモデル選択、28 分でアーキテクチャ、34 分でガバナンスへ移ります。モデル待ちが長い場合は、末尾の「止まったときの切り替え」にある操作とセリフを使います。独立した質疑応答枠を取る場合は、後述の 30 分版に 10 分を加えます。

## 0. スライドから実物へ

**時間:** 0:00～1:00。導入 30 秒、画面上で今日追うポイントを示す 30 秒。

- **スライドから完成形へ切り替える**

  **操作:** タスクバーから Edge/Chrome へ切り替え、`http://localhost:5070/` のチャットタブを開く（一番目、`Ctrl+1`）。ブラウザーを最大化し、左上の `Retail Analytics Assistant` を指す。スライドファイルは閉じない。

  **トーク:** 「ここまでは SDK の構成を説明しました。ここからは、既存の業務アプリへ組み込んだ実物に切り替えます。こちらが Retail Analytics Assistant です。小売の取引や顧客セグメントを、自然言語で確認するアプリです。」

- **画面の三つの接点を紹介する**

  **操作:** ブラウザーの Retail Analytics Assistant で、下部の入力欄、右上の `Model:`、中央の回答領域を順に指す。

  **トーク:** 「利用者は、ここに業務上の質問を入力します。回答に使うモデルは、この選択欄で指定します。回答はここに順次表示されます。完成形を見た後、この表示、モデル選択、業務ツールへの接続をコードで追います。」

**画面を止めて話す:**

> 今日は「どのモデルが一番賢いか」ではなく、「入力から業務データにたどり着き、回答を返すまでを、どこでアプリにつなぐか」に注目してください。最後は、その接続にどんな制御が必要かまで見ます。

## 1. 完成形を見せる

**時間:** 1:00～6:00。画面紹介と質問 1 分、応答の観察 1 分、MCP ログ 1 分、データとの照合 1 分、確認とつなぎ 1 分。応答が早ければ説明を進め、待ち時間を埋めるためだけに追加送信しません。

**入力する質問:** 事前にコピーしておき、次の項目の「貼り付け」で使います。

```text
取引データを参照して、購入金額の合計が大きい顧客の上位3件を、顧客IDと金額で教えてください。日本語で簡潔に回答してください。
```

- **購入額上位の顧客について質問を送る**

  **操作:** ブラウザーのチャット画面。`Model:` をクリックし、リハーサルで使えたモデルを選択する。下部の入力欄をクリックし、上の質問を `Ctrl+V` で貼り付ける。入力欄で Enter、または右側の送信ボタンを一度クリックする

  **トーク:** 「最初は事前に確認したモデルを使います。購入合計が大きい顧客の上位三件を、実データを参照して答えてもらいます。この内容で送信しますので、回答が出る様子を見てください。」

- **回答を待ちながら説明する**

  **操作:** ブラウザーのチャット画面。中央の回答領域を表示したまま、最初の本文を待つ

  **トーク:** 「このアプリは、小売データを読むツールを接続しています。本文が出る前にデータ取得が必要になる場合もあり、まだ表示がないだけでは失敗とは判断しません。」

- **届いた回答を観察する**

  **操作:** ブラウザーのチャット画面。本文が出始めたら、その文章へポインターを置く。入力欄が再び有効になったら、回答中の顧客 ID と金額を指す

  **トーク:** 「回答が届き始めました。全文の完成を待たず、生成された部分から表示しています。顧客 ID と金額が返りました。この数字は、後ほど元のデータとも照合します。」

- **データ取得ツールのログを確認する**

  **操作:** VS Code の API ログ用ターミナル。VS Code に切り替え、「表示」→「ターミナル」で `API` を選ぶ。ターミナル上部の境界を上へドラッグし、ログを読める高さにする。ターミナル内をクリックして `Ctrl+F`、`MCP tool call:` を入力。最新の要求に対応する行へ移動し、Esc で検索を閉じる。今回の `retail-analytics/` の行を確認できた場合だけ、サーバー名とツール名を指す

  **トーク:** 「API のログへ移ります。MCP tool call が、ツール呼び出しの目印です。今回の送信に対応する行を探します。」

  **確認できたら:** 「この行に、業務データ用のツール呼び出し開始が記録されています。開始したことと、取得の成功や回答の正確さは分けて確認します。」

- **ログの出力元を見せる場合**

  **操作:** VS Code のコード画面: 任意。出力元を聞かれた場合だけ、[app/services/copilot_chat.py:189～197](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L189-L197) を開く。`Ctrl+G` → `189` → Enter

  **トーク:** 「ログを書いているのはこのイベント処理です。194 行目の書式へ、サーバー名とツール名を渡しています。」

- **ツール利用を確認できない場合**

  **操作:** ブラウザーのチャット画面: ログなし。ブラウザーへ戻り `Ctrl+1`。入力欄に同じ質問と「必ず利用可能な小売データのツールで確認してください」を貼り付け、一度だけ送信する

  **トーク:** 「今のログだけではツール利用を確認できないので、データ取得を明示して一度だけ確かめます。」

- **再試行でも確認できない場合**

  **操作:** 再試行でもツール利用を確認できなければ、VS Code の「表示」→「ターミナル」でラボ用 PowerShell の `LAB` を選び、次の取引 API の確認へ進む。起動中の uvicorn がある `API` ターミナルには入力しない。

  **トーク:** 「この実行ではツール利用を確認できませんでした。成功扱いにはせず、元の業務データと接続コードから構成を説明します。」

**発表者メモ:** ツール名・呼び出し回数・回答文は固定しません。30 秒ほど反応がない場合、または空の回答で終わった場合は、末尾の「止まったときの切り替え」のセリフを使います。

### 回答をデータと照合する

**投影する画面:** **VS Code の統合ターミナル（PowerShell）**。ブラウザーの API 確認画面は開きません。uvicorn を起動したまま、別のラボ用 `LAB` ターミナルから HTTP GET を実行します。

- **ターミナルで C003 の取引を取得する**

  **操作:** VS Code の「表示」→「ターミナル」で `LAB` の PowerShell を選ぶ。前のラボが終了し、入力待ちであることを確認して、次の一行を貼り付けて Enter。`API` ターミナルや Bash には入力しない。

  ```powershell
  (Invoke-RestMethod -Uri 'http://localhost:5070/api/transactions' -TimeoutSec 10 -ErrorAction Stop) | Where-Object { $_.customerId -eq 'C003' } | Format-Table customerId, amount, productCategory -AutoSize
  ```

  **トーク:** 「答え合わせは VS Code のターミナルで行います。既存の取引 API を GET で呼び、返ってきた一覧から C003 の行だけを表示します。モデルは使わず、データも更新しません。」

- **C003 の購入金額を確かめる**

  **操作:** VS Code の `LAB` ターミナルに表示された `customerId` と `amount` の列を指す。未変更のシードなら C003 の 2 行に `1250` と `450` がある。表示の小数桁や行順は固定しない。エラーや空の結果なら、値が取得できたとは言わず末尾の切り替え手順を使う。

  **トーク:** 「ここが API から取得した取引です。customerId が顧客、amount が一件の購入金額です。初期データなら 1,250 と 450 の二件で合計 1,700。現在表示されている実データを基準に回答を確かめます。」

- **チャットの回答と照合する**

  **操作:** VS Code のターミナルに結果を残したまま、Edge/Chrome の Retail Analytics Assistant（`http://localhost:5070/`、一番目のタブ）へ戻る。中央の会話をスクロールし、先ほどの回答の C003 と購入合計を指す。

  **トーク:** 「元の取引を確認したので、回答へ戻って同じ顧客の金額を照合します。自然な文章であることと、数字が合っていることは別々に確認します。」

- **数字が一致しない場合**

  **操作:** 値が一致しない場合は、ブラウザーの回答と VS Code の `LAB` ターミナルに残した取引結果を見比べる。再送信や DB の変更はしない。

  **トーク:** 「ここは元データと回答が一致していません。取得範囲や説明を確認する必要があります。文章が返ったことだけで成功とはしません。」

**発表者メモ:** DB が変更済みなら今回のターミナル出力を正とし、初期値を断定しません。エラーや空の結果は成功と扱いません。HTTP の取得に失敗した場合は、末尾の「API がエラーを返したとき」へ進みます。

**画面を止めて話す:**

> ログ、戻ってきた回答、業務データを組み合わせて確認します。ツール呼び出し開始のログだけで、取得の成功や最終回答の正確さまでは証明できません。

**短い問いかけ:** 「この画面で、モデルに任せてよいのはどこで、アプリ側に残したいのはどこでしょうか？」

**回収する答え:**

> 質問の解釈や説明文の作成はモデルが担います。一方で、データ取得の方法や許可する操作はアプリ側で定義します。この役割分担を、ここからコードで確認します。

- **完成形からストリーミングのコードへ移る**

  **操作:** ブラウザーのチャット画面 → VS Code のコード画面。6 分を目安に VS Code へ切り替え、`Ctrl+P` に `src/AgentOrchestrator-python/app/services/copilot_chat.py` と入力して Enter、`Ctrl+G` → `157` → Enter

  **トーク:** 「ここまでが利用者に見える完成形です。ここからは、この回答を画面へ届ける仕組みを、SDK のセッション作成から見ていきます。」

## 2. ストリーミングを掘る

**時間:** 6:00～14:00。SDK サービス 3 分、SSE 1 分、ブラウザー受信 1 分、イベントラボ 2 分、確認とつなぎ 1 分。

### 2-1. SDK のイベントから API へ

- **セッション作成とストリーミング設定を見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/services/copilot_chat.py` → Enter。`Ctrl+G` → `157` → Enter。[app/services/copilot_chat.py:157～173](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L157-L173) が入るようスクロール。163 行目の `create_session`、165 行目の `streaming=True` の順に指す。同じ設定内の `mcp_servers` と `on_permission_request` を短く指す

  **トーク:** 「まず API の内側にある Python の SDK サービスです。セッションを作り、streaming を true にして、生成途中の本文を受け取ります。ただし、これだけでブラウザー配信まで完成するわけではありません。業務ツールと権限の設定には後で戻り、まず本文を追います。」

- **本文の差分を受け取る処理を見る**

  **操作:** VS Code のコード画面。`Ctrl+G` → `178` → Enter。[app/services/copilot_chat.py:178～188](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L178-L188) の 182～183 行目を指す

  **トーク:** 「次はイベントを受ける関数です。本文の差分が届くと、delta_content をキューへ入れています。SDK はこの関数を呼ぶ形で通知します。」

- **完了・エラーと待機の関係を見る**

  **操作:** VS Code のコード画面。`Ctrl+G` → `198` → Enter。[app/services/copilot_chat.py:198～209](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L198-L209) の `SESSION_IDLE` と `SESSION_ERROR` を指す。同じ範囲の 206 行目 `session.on`、208 行目 `session.send`、209 行目 `await done` を指す

  **トーク:** 「本文とは別に、処理の完了と異常もイベントで扱います。idle になれば待機を終え、エラーなら例外として受け取ります。購読を登録してから質問を送信し、完了イベントを待ちます。送信メソッドを呼んだだけでは、回答が完成したとは扱いません。」

- **キューから API へ本文を渡す**

  **操作:** VS Code のコード画面。`Ctrl+G` → `223` → Enter。[app/services/copilot_chat.py:223～228](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L223-L228) の `queue.get` と `yield item` を指す

  **トーク:** 「キューに入った本文は、こちらで順に取り出します。この yield が、次に見る Web API 側へ本文を渡す接続点です。」

**画面を止めて話す:**

> キューがあるのは、SDK が「届いたら関数を呼ぶ」方式で、Web API が「次の値を取り出す」方式だからです。この違いをサービスの中で吸収しています。

### 2-2. SSE とブラウザー描画

- **FastAPI で SSE に変換する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/routers/chat.py` → Enter。`Ctrl+G` → `124` → Enter。[app/routers/chat.py:124～140](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py#L124-L140) を表示する。129 行目の `data:`、131 行目の `[DONE]` を指す。134 行目の `error` と 136～140 行目の `StreamingResponse` を指す

  **トーク:** 「次は FastAPI のルーターです。本文の断片を JSON にし、SSE の data フレームに包んで返します。正常終了時は DONE、途中の異常は error を送ります。レスポンスの種類は text/event-stream。ここでブラウザー向けの形式に変換しています。」

- **ブラウザーで応答を読み取る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/static/app.js` → Enter。`Ctrl+G` → `170` → Enter。[app/static/app.js:170～188](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L170-L188) の POST と `getReader` を指す。同じ範囲の `buffer`、`split`、`lines.pop` を指す

  **トーク:** 「今度はブラウザーで動く JavaScript です。質問を POST し、レスポンスを getReader で少しずつ読み取ります。ネットワークの一回の読み取りで、必ず一つのメッセージがそろうとは限りません。行の途中で切れた分は、次の読み取りまで残しています。」

- **受信した本文を画面に反映する**

  **操作:** VS Code のコード画面。`Ctrl+G` → `190` → Enter。[app/static/app.js:190～199](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L190-L199) の `data:` 判定と `content += chunk.content` を指す。`Ctrl+G` → `162` → Enter。[app/static/app.js:162～167](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L162-L167) の `setInterval` と `50` を指す

  **トーク:** 「SSE の行から本文を取り出し、ここで回答の文字列へ追加します。SDK のイベントをブラウザーが直接受けているのではありません。受信した本文の描画は、約 50 ミリ秒ごとにまとめます。受信頻度と再描画頻度を分けて、画面更新の負担を抑えています。」

**画面を止めて話す:**

> SDK の差分一件、ネットワークの読み取り一回、画面の再描画一回は、同じ単位ではありません。その間をつないで、最初に見た表示を作っています。

### イベントラボを実演する

**実行コマンドの控え:** 次の操作にも同じコマンドを記載しています。末尾に `--model` と確認済み ID を付ける場合は、事前準備時に決めておきます。

```shell
uv run python -m sdk_labs events
```

- **イベントラボを実行する**

  **操作:** VS Code の「表示」→「ターミナル」で、ラボ用の `LAB` を選ぶ。作業場所が `src/AgentOrchestrator-python/` で、前のコマンドが終わっていることを確認し、`uv run python -m sdk_labs events` を入力して Enter。API ログ用の `API` ターミナルには入力しない。

  **トーク:** 「API は動かしたまま、別のターミナルで小さなラボを実行します。UI を外して、SDK のイベント自体を見ます。このコマンドは小売の KPI を二つ聞くサンプルです。今回はデータ取得ではなく、イベントの流れだけを観察します。」

- **ラボで使うモデルを確認する**

  **操作:** VS Code のラボ・テスト用ターミナル。`Model:` が出たら指し、出力待ちの間もターミナルを表示する

  **トーク:** 「ここに実際に選ばれたモデルが表示されます。ブラウザーのモデル選択とは別なので、ラボ側の表示も確認します。」

- **差分イベントを数えるコードを見る**

  **操作:** VS Code のコード画面。待機中に `Ctrl+P` → `src/AgentOrchestrator-python/sdk_labs/events_sample.py` → Enter、`Ctrl+G` → `21` → Enter。[sdk_labs/events_sample.py:21～40](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py#L21-L40) を表示する。30 行目の差分カウントと 40 行目の件数表示を指す

  **トーク:** 「待っている間に、何を表示するコードかを見ます。Web アプリと同じく、streaming を true にしています。差分は一件ずつ画面に出すのではなく、件数を数えています。表示が少なくても、差分が届いていないという意味ではありません。」

- **イベントの実出力を確認する**

  **操作:** VS Code のラボ・テスト用ターミナル。`LAB` ターミナルをクリックし、出力中の `assistant.message`、`session.idle` を探す。確認できたものだけ指す。VS Code のラボ・テスト用ターミナル → VS Code のコード画面。最後の `Total delta events` を指す。必要ならエディターへ戻り `Ctrl+G` → `53` → Enter。[sdk_labs/events_sample.py:53](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py#L53) と対応づける

  **トーク:** 「こちらが実際のイベント出力です。完成した本文の通知と、セッションが処理を終えた通知を区別して見ます。最後が本文の差分通知の総数です。これはトークン数や課金件数ではありません。表示しているのは、このカウンターの値です。」

- **完了・エラー・タイムアウトを確認する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/sdk_labs/_common.py` → Enter、`Ctrl+G` → `16` → Enter。[sdk_labs/_common.py:16～35](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py#L16-L35) の 26・30・35 行目を順に指す

  **トーク:** 「ラボの待機処理も見ます。完了で待機を終え、エラーは例外にし、最後の wait_for にはタイムアウトを付けています。Web アプリがこの共通クラスを使っているわけではありません。」

- **ラボが完了しない場合**

  **操作:** ラボが完了しなければ、VS Code の `LAB` ターミナルで `Ctrl+C` を一度押す。以降はイベントラボの事前記録を画像ビューアーで開く。記録がなければ VS Code の [sdk_labs/events_sample.py](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py) のイベント処理を表示する。コード表示だけの場合は、次のセリフから「事前記録」を省く。

  **トーク:** 「ライブのイベント出力が完了していないので、ここからは事前記録、またはコードで確認できる範囲を説明します。今の実行が成功したとは扱いません。」

**発表者メモ:** 出力の種類・順序・件数は固定しません。「事前記録」がない場合は、その部分のセリフを省いて「コードで確認できる範囲」と読みます。実行が継続している VS Code のラボ・テスト用ターミナル に次のコマンドを入力しないでください。終了できない場合の操作は末尾の切り替え手順にあります。

**短い問いかけ:** 「`streaming=True` だけでブラウザーへの配信まで完成するでしょうか？」

**回収する答え:** 「SDK イベントを受け取り、API で SSE に変換し、UI で読むところまでアプリが実装します。」

- **チャット画面へ戻ってモデル選択へ進む**

  **操作:** VS Code のコード画面 → ブラウザーのチャット画面。14 分を目安にブラウザーへ切り替え、`Ctrl+1`

  **トーク:** 「回答を届ける仕組みを確認できたので、利用画面へ戻ります。次は、画面で選んだモデルがどこに渡るかです。」

## 3. モデル選択を掘る

**時間:** 14:00～19:00。モデル選択と再送 1 分、設定経路の説明 2 分、結果の比較 1 分、確認とつなぎ 1 分。

- **同じ質問を別モデルで送る**

  **操作:** Edge/Chrome の Retail Analytics Assistant（`http://localhost:5070/`）へ戻る。前の回答終了後、右上の `Model:` で別の確認済みモデルを選ぶ。下部の入力欄に「取引データを参照して、購入金額の合計が大きい顧客の上位3件を、顧客IDと金額で教えてください。日本語で簡潔に回答してください。」を貼り付け、Enter で送信する。

  **トーク:** 「次の質問では、別の確認済みモデルを使います。処理中のセッションを切り替える操作ではなく、次の送信に使うモデルを選びます。質問とデータは同じにして、モデルだけを変えて送ります。回答を待つ間に、選択した値の行き先を追います。」

- **画面のモデル一覧と送信内容を見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/static/app.js` → Enter、`Ctrl+G` → `113` → Enter。[app/static/app.js:113～142](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L113-L142) の 116 行目を指す。同じファイルで `Ctrl+G` → `170` → Enter。[app/static/app.js:170～174](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L170-L174) の `selectedModel` を指す

  **トーク:** 「モデルの一覧は、画面からこの API へ問い合わせています。まず一覧を作る入口を見ます。送信時には、選んだモデル ID を質問と一緒に渡しています。画面上の選択が、このリクエストの値になります。」

- **モデル一覧 API の取得とフォールバックを見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/routers/chat.py` → Enter、`Ctrl+G` → `84` → Enter。[app/routers/chat.py:84～108](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py#L84-L108) のライブ取得と末尾の固定一覧を指す

  **トーク:** 「一覧 API はライブ取得を優先します。取得できない場合は固定の候補へ戻るので、表示されていることだけでは利用可能性の保証にはなりません。」

- **SDK のモデル取得とセッション設定を追う**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/services/copilot_chat.py` → Enter、`Ctrl+G` → `132` → Enter。[app/services/copilot_chat.py:132～140](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L132-L140) の `list_models()` を指す。同じファイルで `Ctrl+G` → `163` → Enter。[app/services/copilot_chat.py:163～173](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L163-L173) の `model=model` を指す

  **トーク:** 「ライブ一覧の取得元は、SDK の list_models です。接続しているランタイムへモデルを問い合わせます。最終的にこの値が、セッションを作るときの model に入ります。このアプリでは送信ごとに新しいセッションを作っています。」

- **二つの回答を比較する**

  **操作:** ブラウザーのチャット画面。ブラウザーへ切り替え `Ctrl+1`。中央の会話領域でホイールを使い、最初の回答と今回の回答を順に表示する。二つの回答の表、箇条書き、説明の長さを順に指す

  **トーク:** 「回答へ戻ります。まず顧客 ID と合計金額を比べます。同じデータなら一致してほしい事実です。文章の構成や詳しさは変わる可能性があります。こちらは表現の違いとして見ます。今回一回の応答速度や書き方だけで、モデルの優劣や費用は断定しません。」

- **設定したモデルをログでも確認する場合**

  **操作:** VS Code の API ログ用ターミナル: 任意。`API` ターミナルを選び、`Ctrl+F` に `Creating session with model:` を入力して今回の行を探す。Esc で検索を閉じ、モデル ID を指す。VS Code のコード画面: 任意。ログのコードも見せる場合はサービスの `Ctrl+G` → `155` → Enter。[app/services/copilot_chat.py:155](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L155) を指す

  **トーク:** 「設定されたモデル ID は、API のセッション作成ログでも確認できます。画面の選択と、API が受け取った値を対応づけています。この行がモデル ID のログを出しています。性能測定ではなく、どの設定で作成したかの確認です。」

- **確認済みモデルが一つだけの場合**

  **操作:** 確認済みモデルが一つだけなら再送しない。VS Code の `Ctrl+P` に `src/AgentOrchestrator-python/app/services/copilot_chat.py` を入力して Enter、`Ctrl+G` → `164` → Enter。[app/services/copilot_chat.py:164](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L164) の `model=model` を指す。

  **トーク:** 「今日は別モデルでの実行比較はせず、切り替えの接続点までを示します。ここへ別のモデル ID を渡す構成です。」

- **別モデルでの実行に失敗した場合**

  **操作:** ブラウザーのチャット画面: 別モデル失敗。失敗時は別モデルを次々試さず、最初に成功した回答を会話領域で表示する

  **トーク:** 「今回の別モデルでの回答は確認できなかったので、最初の結果へ戻します。切り替えられる設計と、当日実行できることは分けて確認が必要です。」

**画面を止めて話す:**

> 今変えたのは、モデル ID です。データベースや業務ツールの実装は変えていません。モデルを差し替えられる接続点を持つことと、どのモデルでも期待する品質になることは別です。後者は、実際の業務質問を使って評価します。

**短い問いかけ:** 「モデル一覧を固定で書く場合、何が困るでしょうか？」

**回収する答え:** 「提供状況やアカウントの利用可否が変わると、表示と実態がずれます。そのためライブ取得を優先し、フォールバック表示も利用可能性の保証とは扱いません。」

- **ツールの最小例へ移る**

  **操作:** ブラウザーのチャット画面/VS Code のコード画面 → VS Code のラボ・テスト用ターミナル。19 分を目安に VS Code の `LAB` ターミナルを選ぶ。前のコマンドが終わり、入力待ちであることを確認する

  **トーク:** 「モデルを変えても、業務データへの接続をモデルごとに書き直す必要はありません。次は、その接続点であるツールを小さな例から見ます。」

## 4. ツール呼び出しを掘る

**時間:** 19:00～28:00。直接登録のツールラボ 3 分、Web アプリの MCP 接続 3 分、既存処理の再利用 1 分、API との照合 1 分、確認とつなぎ 1 分。

### 4-1. 最小のツールを先に見せる

**実行コマンドの控え:** 次の操作にも同じコマンドを記載しています。

```shell
uv run python -m sdk_labs tools
```

- **直接登録ツールのラボを実行する**

  **操作:** VS Code のラボ用 `LAB` ターミナルを選ぶ。作業場所が `src/AgentOrchestrator-python/` で、入力待ちのプロンプトに戻っていることを確認し、`uv run python -m sdk_labs tools` を入力して Enter。API ログ用ターミナルは操作しない。

  **トーク:** 「まず Python 関数を直接登録する最小例を実行します。API は動かしたまま、別のラボで関数呼び出しを確認します。」

- **引数とツール関数を見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/sdk_labs/tools_sample.py` → Enter、`Ctrl+G` → `37` → Enter。[sdk_labs/tools_sample.py:37～57](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/tools_sample.py#L37-L57) のパラメータークラスと 45 行目を指す。同じ範囲の 48 行目 `@define_tool`、合計処理、55 行目の `print` を順に指す

  **トーク:** 「この Pydantic モデルが引数の定義です。顧客 ID を受け取ることと、その意味を説明しています。モデルに渡す操作の契約に当たります。この関数をツールとして登録します。購入額を合計するのは Python 関数で、print は実行されたことを観察するためのログです。」

- **セッションへの登録と権限設定を見る**

  **操作:** VS Code のコード画面。`Ctrl+G` → `68` → Enter。[sdk_labs/tools_sample.py:68～76](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/tools_sample.py#L68-L76) の `tools=[get_customer_total]` を指す。同じ範囲の 75 行目 `PermissionHandler.approve_all` を指す

  **トーク:** 「定義しただけではなく、セッションの tools にこの関数を渡しています。モデルは用途の説明を見て、必要な顧客 ID で呼び出しを要求します。ここは学習用に広く承認する設定です。Web アプリの限定的なハンドラーとは違うので、そのまま業務用の権限設計として扱いません。」

- **ツールの結果と回答を確認する**

  **操作:** VS Code のラボ用 `LAB` ターミナルへ戻り、今回の `Model:` と `[tool] get_customer_total(C003)` を探す。ログに `C003` と `$1,700.00` がある場合だけ、続く `Assistant:` の本文と比較する。

  **トーク:** 「実際の出力に戻ります。モデル名に加えて、Python 関数からの tool ログが出ているかを確認します。」

  **確認できたら:** 「C003 を指定した関数が、合計 1,700 を返しています。その結果を受け取って、モデルが回答文にしています。」

- **ツールの結果が確認できない場合**

  **操作:** VS Code のラボ・テスト用ターミナル: 未確認時。tool ログや回答が出なければ、再実行せず VS Code のコード画面の関数本体へ戻る

  **トーク:** 「この実行ではツールの結果を確認できていません。期待値を実行結果とは扱わず、コードがどう登録されるかを説明します。」

**発表者用の期待値:** 以下は未変更サンプルの期待値で、ターミナルの実出力の代わりにはしません。

```text
[tool] get_customer_total(C003) -> $1,700.00
```

**画面を止めて話す:**

> このラボのデータはメモリ上の固定値で、Web アプリの SQLite を読んでいません。「説明と引数を持つ関数を呼び、その結果で答える」という関係を、次は別プロセスの業務ツールで見ます。

### 4-2. Web アプリの MCP 接続を追う

**Retail Analytics Assistant に送る質問:**

```text
顧客C002の購入実績と予測セグメントを、利用可能な小売データのツールで確認してください。購入合計、予測セグメント、判定の根拠を日本語で簡潔に教えてください。
```

- **チャットで C002 の実績と予測を聞く**

  **操作:** Edge/Chrome の Retail Analytics Assistant（`http://localhost:5070/`）へ戻る。前の回答終了後、下部の入力欄に「顧客C002の購入実績と予測セグメントを、利用可能な小売データのツールで確認してください。購入合計、予測セグメント、判定の根拠を日本語で簡潔に教えてください。」を貼り付け、Enter。

  **トーク:** 「Web アプリへ戻り、今度は C002 の購入実績とセグメントを聞きます。ラボの固定データではなく、業務データを読むツールにつなぎます。」

- **MCP サーバーの起動設定を見る**

  **操作:** VS Code のコード画面。待機中に `Ctrl+P` → `src/AgentOrchestrator-python/app/services/copilot_chat.py` → Enter、`Ctrl+G` → `69` → Enter。[app/services/copilot_chat.py:69～76](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L69-L76) を表示。71 行目 `sys.executable`、72 行目 `-m mcp_server`、73 行目 `working_directory` を順に指す。74 行目の `tools: ["*"]` を指す

  **トーク:** 「回答を待つ間に、接続設定を見ます。retail-analytics という名前で、ローカルの MCP サーバーを登録しています。API と同じ Python で mcp_server モジュールを起動し、作業ディレクトリも指定します。接続先の起動方法を、ここで決めています。星印は、この MCP サーバーが公開する全ツールという意味です。すべてのサーバーや任意の OS 操作を許可する意味ではありません。」

- **MCP 設定をセッションへ渡す**

  **操作:** VS Code のコード画面。`Ctrl+G` → `162` → Enter。[app/services/copilot_chat.py:162～173](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L162-L173) の 169 行目を指す

  **トーク:** 「この設定をセッション作成時の mcp_servers に渡します。最初に見たストリーミング設定と、同じセッションへ組み込んでいます。」

- **顧客サマリーの取得と集計を見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/mcp_server/server.py` → Enter、`Ctrl+G` → `147` → Enter。[mcp_server/server.py:147～158](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L147-L158) の説明・`customer_id`・クエリを指す。`Ctrl+G` → `171` → Enter。[mcp_server/server.py:171～181](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L171-L181) の `totalSpend`、`averageSpend` を指す

  **トーク:** 「こちらが別プロセス側のツール定義です。顧客 ID を受け取り、その顧客の取引を取得します。自由な SQL の入口ではなく、業務として定義した関数を公開しています。取得した実績から合計と平均を計算し、結果を返します。この値を使って、モデルが利用者向けの文章を組み立てます。」

- **既存の予測処理へつながる箇所を追う**

  **操作:** VS Code のコード画面。`Ctrl+G` → `183` → Enter。[mcp_server/server.py:183～193](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L183-L193) の予測ツールと 192 行目を指す。`Ctrl+P` → `src/AgentOrchestrator-python/app/services/retail_analytics.py` → Enter、`Ctrl+G` → `83` → Enter。[app/services/retail_analytics.py:83～102](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py#L83-L102) を表示。`Ctrl+G` → `105` → Enter。[app/services/retail_analytics.py:105～131](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py#L105-L131) を表示し、125 行目 `avg_spend < 50` を指す

  **トーク:** 「次は予測ツールです。注目してほしいのはこの一行で、MCP 側に判定を再実装せず、既存の RetailAnalyticsService を呼んでいます。呼び出し先の既存サービスへ移ります。ここで取引を集計し、購入額や頻度を計算しています。今回は学習済みの予測モデルではなく、ルール判定です。初期データの C002 は平均購入額が 50 未満なので、この At Risk の分岐に入ります。」

- **実際のツール呼び出しと回答へ戻る**

  **操作:** VS Code の API ログ用ターミナル。`API` を選び、`Ctrl+F` で `MCP tool call:` を検索し、今回の要求のツール名を確認する。ブラウザーのチャット画面。ブラウザーで `Ctrl+1`、最新の C002 の回答まで会話領域をスクロールする

  **トーク:** 「API ログへ戻り、今回どのツールが呼ばれたかを確認します。呼び出し順序や回数は固定せず、実際に出ている行だけを見ます。回答に戻りました。ここに出た実績と予測を、次は既存の予測 API と照合します。」

**次の三項目は質問された場合だけ:** 開くのは Python 版の [mcp_server/server.py](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py) です。本編ではこの三項目を読み飛ばします。

- **取引一覧ツールについて質問された場合**

  **操作:** VS Code のコード画面: 任意。`Ctrl+G` → `115` → Enter。[mcp_server/server.py:115～127](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L115-L127) の `list_transactions` を指す

  **トーク:** 「取引一覧のツールもあります。顧客で絞り込めて、返す件数には上限を設けています。」

- **取引一件の取得について質問された場合**

  **操作:** VS Code のコード画面: 任意。`Ctrl+G` → `129` → Enter。[mcp_server/server.py:129～136](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L129-L136) の `get_transaction` を指す

  **トーク:** 「こちらは取引 ID で一件だけ取得するツールです。業務上の取得単位で分けています。」

- **セグメント一覧について質問された場合**

  **操作:** VS Code のコード画面: 任意。`Ctrl+G` → `138` → Enter。[mcp_server/server.py:138～145](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L138-L145) の `list_segments` を指す

  **トーク:** 「こちらは登録済みセグメントの一覧です。顧客単位の予測ツールとは別に、セグメントの規模や継続率を参照します。」

### 4-3. 既存 API と答え合わせする

- **ターミナルで C002 の予測を実行する**

  **操作:** VS Code の「表示」→「ターミナル」でラボ用 PowerShell の `LAB` を選ぶ。前のコマンドが終了していることを確認して、次の一行を貼り付けて Enter。URL の末尾の `C002` が対象顧客。起動中の `API` ターミナルには入力しない。

  ```powershell
  Invoke-RestMethod -Uri 'http://localhost:5070/api/segments/predict/C002' -TimeoutSec 10 -ErrorAction Stop | Format-List customerId, predictedSegment, confidence, topFeatures
  ```

  **トーク:** 「同じくターミナルから、C002 の予測 API を呼びます。チャットに聞いた顧客と同じ ID を指定しています。こちらはモデルを呼ばず、既存の判定ルールだけを実行します。」

- **予測の実行結果と根拠を確認する**

  **操作:** VS Code の `LAB` ターミナルに結果が表示されたら、`customerId` と `predictedSegment`、続いて `confidence` と `topFeatures` を指す。未変更シードでは `C002`、`At Risk`、`0.62` が目安。値は今回の API 応答を優先し、エラーが出ていたら次の成功説明は読まない。

  **トーク:** 「ここに出た predictedSegment が、既存 API の判定です。confidence と判定の根拠も確認できます。confidence はルールに埋め込まれた値で、検証済みの正解確率という意味ではありません。」

- **チャットの説明と照合する**

  **操作:** VS Code の `LAB` ターミナルに予測結果を残し、Edge/Chrome の Retail Analytics Assistant（`http://localhost:5070/`、一番目のタブ）へ戻る。C002 の回答のセグメント名と根拠を、ターミナルの結果と比較する。

  **トーク:** 「チャットへ戻って、同じ結果を説明できているかを見ます。判定の実装を共有しても、説明文の正確さは別に確認します。」

**画面を止めて話す:**

> 直接登録のラボは、同じ Python プロセス内の関数と固定データでした。Web アプリは、別プロセスの MCP サーバーを通じて SQLite と既存処理につながります。接続方法は違っても、業務操作を関数として定義する考え方は共通です。

**短い問いかけ:** 「自分のアプリなら、最初にどんな読み取り専用ツールを公開しますか？」

**回収する答え:** 「たとえば、顧客の購入履歴を取得する、注文の状態を調べる、といった操作です。用途と権限を絞った業務操作から考えます。」

- **システムマップへ移る**

  **操作:** ブラウザーのチャット画面 → ブラウザーのシステムマップ。28 分を目安に `Ctrl+2` でシステムマップのタブへ移る。

  **トーク:** 「ここまで見た UI、API、SDK、業務ツールを、全体図で整理します。」

## 5. アーキテクチャへつなぐ

**時間:** 28:00～32:00。チャット経路 1 分、MCP と REST の比較 1 分、Python の起動構成 1 分、役割分担の確認 1 分。

**マップの操作:** Edge/Chrome に開いた [システムマップ HTML](../system-map/map.html) のタブを使います。以下の各項目で URL 末尾の `#view=...` だけを変えます。自動再生やノードのクリックは使わず、ポインターで経路を示します。

- **チャットの経路を図でたどる**

  **操作:** Edge/Chrome のシステムマップのタブを開く（二番目、`Ctrl+2`）。`Ctrl+L` の後、URL の `#` 以降だけを選び `#view=chat-request-path` に置き換えて Enter。`#` がなければ末尾へ追記する。[チャット経路](../system-map/map.html#view=chat-request-path) で `チャット UI` → `小売 API` → `CopilotChatService` → `GitHub Copilot CLI` → `モデル` を順に指す。

  **トーク:** 「まずチャットの経路です。ブラウザーから FastAPI、その内側のチャットサービスへ渡り、SDK が CLI のランタイムと通信します。Python 版は UI と API を同じ 5070 番で提供しています。ブラウザーへ SDK や認証情報を直接持たせる構成ではありません。」

- **MCP のデータ参照経路へ切り替える**

  **操作:** ブラウザーのシステムマップ。URL の `#` 以降を `#view=model-data-access` に置き換えて Enter。[MCP 経路](../system-map/map.html#view=model-data-access) の `retail-analytics MCP` と `retail.db` を指す

  **トーク:** 「次はモデルが業務データを読む経路です。MCP の業務ツールを呼び、読み取り専用の接続で SQLite を参照します。」

- **通常の REST API の経路へ切り替える**

  **操作:** ブラウザーのシステムマップ。URL の `#` 以降を `#view=rest-and-persistence` に置き換えて Enter。[REST 経路](../system-map/map.html#view=rest-and-persistence) の API、`RetailAnalyticsService`、DB を指す

  **トーク:** 「こちらは通常の業務 API の経路です。アプリ自身の読み書きは従来どおり残っていて、すべてを MCP 経由へ置き換えたわけではありません。」

- **Python アプリの起動構成を確認する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/main.py` → Enter、`Ctrl+G` → `28` → Enter。[app/main.py:28～41](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py#L28-L41) の 37・41 行目を指す。同じファイルで `Ctrl+G` → `58` → Enter。[app/main.py:58～63](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py#L58-L63) のルーター登録と静的ファイル登録を指す

  **トーク:** 「起動コードでも確認します。アプリ全体のチャットサービスを一つ作り、終了時に閉じます。送信ごとのセッションとは、寿命が違います。API を先に登録し、最後に静的 UI を登録しています。Python 版では、UI 用にもう一つ別サーバーを起動する必要はありません。」

- **全体図へ戻って通信の役割を整理する**

  **操作:** ブラウザーのシステムマップ。ブラウザーへ戻り `Ctrl+2`。URL 末尾を `#view=chat-request-path` に戻し、通信経路をポインターでたどる。

  **トーク:** 「全体図へ戻ると、ブラウザーと API は HTTP、SDK と CLI は JSON-RPC、MCP サーバーへの接続は stdio です。この役割分担で一つの体験を作っています。」

**図を止めて補足:**

> 図のチャット API 表記は概要で、今回の UI の実際の送信先は /api/chat/stream です。モデル名も例示です。このローカル構成のプロセス分割は、利用者ごとの認証や OS の隔離まで完成したことを意味しません。

**短い問いかけ:** 「通常の REST API まで MCP 経由に変える必要はあるでしょうか？」

**回収する答え:** 「ありません。既存の業務 API は残し、Agent に必要な操作を別の入り口として公開しています。」

## 6. 利用画面へ戻す

**時間:** 32:00～34:00。利用者の視点で回答を確認する 1 分、履歴とセッションの違いをコードで確認する 1 分。

- **利用者の画面へ戻る**

  **操作:** ブラウザーのチャット画面。`Ctrl+1` でチャットへ戻り、中央の会話をスクロールして C002 の回答を表示する。回答、右上のモデル選択欄、下部の入力欄を順に指す。追加送信はしない

  **トーク:** 「利用者の画面に戻ります。MCP や SQL を知らなくても、ここから業務上の質問を確認できます。何を調べられるかはツール側で、どう届けるかはこの UI で設計しています。既存の顧客詳細画面へ同じ接続を組み込むのは、次の応用です。」

- **ページを再読み込みする**

  **操作:** ブラウザーのチャット画面。回答完了後に `Ctrl+R` で再読み込みする。ロード中はそのまま表示

  **トーク:** 「一度ページを再読み込みします。ここでは会話セッションの再開ではなく、画面の表示がどう保存されるかを確認します。」

- **表示履歴が復元された場合**

  **操作:** ブラウザーのチャット画面: 復元時。前の質問と回答が戻ったら指す

  **トーク:** 「表示が戻りました。これはブラウザーに保存した履歴の復元です。モデルが前の会話を引き継いだ証拠ではありません。」

- **表示履歴が復元されない場合**

  **操作:** ブラウザーのチャット画面: 復元しない場合。履歴が戻らなければ、再読み込みを繰り返さず次のコードへ進む

  **トーク:** 「この環境では表示の復元を確認できなかったので、保存と送信のコードを見ます。ブラウザー保存領域の状態も別に確認が必要です。」

- **履歴保存と API への送信を比較する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/app/static/app.js` → Enter、`Ctrl+G` → `47` → Enter。[app/static/app.js:47～59](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L47-L59) の `localStorage` を指す。同じファイルで `Ctrl+G` → `170` → Enter。[app/static/app.js:170～174](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L170-L174) の送信本文を指す

  **トーク:** 「ここでブラウザーの localStorage へ保存し、読み戻しています。これは UI の状態を残す処理です。一方、API に送るのは今回の prompt と model です。過去の表示履歴は送っていないので、継続会話には別途セッション管理が必要です。」

**画面を止めて話す:**

> そのため、デモの質問は「その顧客は？」ではなく「顧客 C002 は？」のように単独で意味が分かる形にしています。SDK にできることと、このアプリに実装したことを分けて見てください。

- **権限制御のコードへ移る**

  **操作:** VS Code のコード画面。34 分を目安に `Ctrl+P` → `src/AgentOrchestrator-python/app/services/copilot_chat.py` → Enter、`Ctrl+G` → `79` → Enter

  **トーク:** 「業務データにつながる以上、何を許すかも重要です。最後に、権限を判定するコードへ移ります。」

## 7. ガバナンスへつなぐ

**時間:** 34:00～39:00。権限ハンドラー 1 分半、DB 設定と既存テスト 1 分半、フック 1 分半、本番向けの確認事項 30 秒。

### 7-1. 今のアプリで実装している制御

- **権限ハンドラーの承認条件を確認する**

  **操作:** VS Code のコード画面。サービスの [app/services/copilot_chat.py:79](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L79) を表示し、`Ctrl+G` → `89` → Enter。[app/services/copilot_chat.py:89～104](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L89-L104) を画面に入れる。93 行目の要求型、94 行目のサーバー名、95 行目の読み取り専用属性を順に指す。97 行目の承認と 102～104 行目の拒否を指す

  **トーク:** 「この関数が、届いた権限要求に対して許可・拒否を判断する部分です。プロンプトのお願いだけでなく、実行時の条件をコードに置いています。MCP の要求であること、自分たちの retail-analytics サーバーであること、読み取り専用であることを確認しています。この条件を満たす要求は一回承認し、その他は拒否する実装です。このハンドラーが受け取る要求に対する判定です。」

- **管理設定の分岐を確認する**

  **操作:** VS Code で Python 版の [app/services/copilot_chat.py:89～90](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L89-L90) を表示し、`Ctrl+G` → `89` → Enter。`managed_settings_enabled` の条件と `PermissionNoResult()` を指す。

  **トーク:** 「管理設定が有効な場合は、このハンドラー自身では判断を返しません。管理設定を含む全経路を、これだけで検証済みとは扱いません。」

- **読み取り専用接続とツール注釈を比較する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/mcp_server/server.py` → Enter、`Ctrl+G` → `57` → Enter。[mcp_server/server.py:57～71](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L57-L71) の 71 行目を指す。同じファイルで `Ctrl+G` → `48` → Enter。[mcp_server/server.py:48](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L48) と、直前の接続設定を対比する

  **トーク:** 「さらに、MCP サーバーの DB 接続を読み取り専用にしています。mode=ro が SQLite 側でも書き込みを拒否します。こちらはツールが読み取り専用だと伝える注釈です。注釈だけに頼らず、接続側にも制約を持たせている点が重要です。」

- **DB の書き込み拒否テストを見る**

  **操作:** VS Code のコード画面。`Ctrl+P` → `src/AgentOrchestrator-python/tests/test_mcp_server.py` → Enter、`Ctrl+G` → `158` → Enter。[tests/test_mcp_server.py:158～177](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_mcp_server.py#L158-L177) の一時ディレクトリ、SELECT、例外検証を指す

  **トーク:** 「その制約を確かめるテストです。一時 DB を作り、読み取りは成功、書き込みは拒否されることを確認します。業務 DB に書き込みを試すわけではありません。」

**実行コマンドの控え:** 次の操作にも同じコマンドを記載しています。

```shell
uv run pytest tests/test_mcp_server.py::test_read_only_engine_rejects_writes -q
```

- **読み取り専用 DB のテストを実行する**

  **操作:** VS Code のラボ用 `LAB` ターミナルを選ぶ。作業場所が `src/AgentOrchestrator-python/` で、前の実行が終了していることを確認し、`uv run pytest tests/test_mcp_server.py::test_read_only_engine_rejects_writes -q` を入力して Enter。結果が出るまでこのターミナルを表示する。

  **トーク:** 「この一件だけを実行します。モデル接続なしで、DB 接続の制約を検証するテストです。拒否してほしい書き込みが、期待どおり例外になることをテストしています。書き込みに失敗することが、このテストでの成功です。」

- **テストが成功した場合**

  **操作:** VS Code のラボ・テスト用ターミナル: 成功時。最後に `1 passed` と表示されたことを確認し、その文字を指す

  **トーク:** 「テストは通りました。この読み取り専用接続では、読み取りができ、書き込みは拒否されることを確認できました。」

- **テストの成功を確認できない場合**

  **操作:** VS Code のラボ・テスト用ターミナル: 失敗・未実行時。成功表示がなければ、テストのコードへ戻る。末尾の切り替え手順に従い、必要なら事前記録を使う

  **トーク:** 「この環境での実行成功は確認できませんでした。ここではテストが何を検証しているかまでを説明し、成功とは言いません。」

**画面を止めて話す:**

> この保証は MCP の DB 接続に対するものです。通常の REST API には更新操作があります。また、読み取り専用は、情報を誰に見せてよいかや、すべてのプロンプトインジェクションを防ぐことの保証ではありません。

### 7-2. 開発時のフックから運用設計へ

- **ガバナンス資料でフックの役割を見る**

  **操作:** ブラウザーのガバナンス資料。ブラウザーへ切り替え `Ctrl+3`。GitHub の文書プレビューで `Ctrl+F` → `ライフサイクルイベント` → Enter、Esc。見出し下の 4 行の表を画面に入れる。表の `preToolUse` と `postToolUse` の行へ順にポインターを置く。

  **トーク:** 「次は開発 Agent 向けのフックの例です。この表で、セッション開始、実行前、実行後、終了の処理を分けています。実行前に許可を判断し、実行後に記録する考え方です。ただし、表があることと、実際のチャットで監査が動いていることは同じではありません。」

- **手元のフック設定を確認する**

  **操作:** VS Code のコード画面。`Ctrl+P` → `.github/hooks/retail-governance.json` → Enter、`Ctrl+G` → `12` → Enter。[.github/hooks/retail-governance.json:12～27](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/hooks/retail-governance.json#L12-L27) の `preToolUse` と 15 行目のスクリプトを指す。同じ範囲の 20 行目 `postToolUse` と 23 行目のスクリプトを指す

  **トーク:** 「ローカルの設定ファイルでは、この実行前イベントにセキュリティゲートのスクリプトを対応づけています。ファイルとイベントの接続を見せています。実行後はこちらの監査用スクリプトです。記録先や機密情報の扱い、失敗時の記録も、運用では設計と検証が必要です。」

- **リモート資料の表示が異なる場合**

  **操作:** ブラウザーのガバナンス資料: 表がない場合。リモート資料が未翻訳などで検索できなければ、ブラウザーのガバナンス資料 を使わず上記の VS Code のコード画面の JSON を表示する

  **トーク:** 「説明資料の表示が異なるので、手元の設定ファイルで示します。実行前と実行後の二つのイベントを見ます。」

**画面を止めて話す:**

> この Python チャットのコードでは SDK のセッションフックを明示登録していません。ランタイム側の読み込みも含め、発火と記録を確認する必要があります。ローカルの JSONL ログと GitHub の組織監査ログも別物です。
>
> 本番では、利用者の認証と閲覧権限、セッションの分離、成功・失敗を追えるログ、ログに残さない情報、監視を設計します。今回はそのすべてを実装したアプリではなく、接続と制御の接点を見ています。

**短い問いかけ:** 「読み取り専用なら、顧客データを誰にでも見せてよいでしょうか？」

**回収する答え:** 「書けないことと、見てよいことは別です。詳しいセキュリティ設計は質疑で扱い、最後に利用者の画面へ戻ります。」

## 8. 締め

**時間:** 39:00～40:00。最初の質問と回答をもう一度見せ、結論に戻ります。新しい送信や新機能の紹介はしません。

- **最初の回答画面へ戻って締める**

  **操作:** ブラウザーのチャット画面。ブラウザーへ切り替え `Ctrl+1`。中央の会話領域を上へスクロールし、最初の購入額上位の質問と回答を画面に入れる

  **トーク:** 「最初の業務画面へ戻ります。この一つの回答の裏側に、ストリーミング、モデル選択、業務ツール、権限の設計がありました。」

**話す:**

> 今日見たのは、チャットを作ること自体が目的のデモではありません。既存の業務アプリに、必要なデータを取りに行って回答する Agent を組み込む例です。
>
> ストリーミングで回答を届け、モデルを選び、ツールで既存処理につなぐ。そして、権限と監査をアプリの責任として設計する。これが Copilot SDK を組み込むときの全体像です。

> 自分のシステムで試すなら、まず「利用者がよく聞く質問」を 1 つ選び、その答えに必要な読み取り専用の業務操作を 1 つつなぐところから始めます。既存の処理を生かして、小さく確かめることができます。

## 発表前の準備

ここは原則として**投影前の準備**で、40 分の本編には含めません。準備の説明を求められた場合も迷わないよう、操作にセリフを付けています。認証操作やトークンは投影しません。

### 起動と疎通

**未起動時のコマンド:** リポジトリルートから一行ずつ実行するための控えです。すでに Python ディレクトリなら `cd` は不要です。uvicorn は起動後も動かしたままにします。

```shell
cd src/AgentOrchestrator-python
uv sync --locked
uv run uvicorn app.main:app --port 5070
```

- **Python の作業場所と依存関係を準備する**

  **操作:** VS Code。「ターミナル」→「新しいターミナル」で PowerShell を開く。`Get-Location` を実行し、リポジトリルートなら上の `cd` を実行する。ターミナル。Python プロジェクト内で `uv sync --locked` を実行し、完了を待つ

  **トーク:** 「まず Python プロジェクトを作業場所にします。SQLite のパスが作業場所に依存するため、起動場所を合わせます。固定済みの依存関係を準備しています。発表直前のアップグレードではなく、リポジトリのバージョンに合わせます。」

- **API を起動してログ用ターミナルを残す**

  **操作:** ターミナル。`uv run uvicorn app.main:app --port 5070` を実行し、`Uvicorn running on` と起動完了の表示を確認する。VS Code の API ログ用ターミナル。ターミナル一覧の当該項目を右クリック →「名前の変更」/ `Rename` → `API`。すでに起動中なら新しく起動せず、そのターミナルを改名する

  **トーク:** 「FastAPI を起動します。この一つのサーバーが、業務 API とチャット UI を提供します。このターミナルは API を動かし続け、ツール呼び出しのログを観察するために残します。」

- **ラボ用のターミナルを分ける**

  **操作:** VS Code のラボ・テスト用ターミナル。新しい PowerShell ターミナルをもう一つ作り、名前を `LAB` にする。`Get-Location` で場所を確認し、必要なら Python プロジェクトへ移動する

  **トーク:** 「実演コマンドは別のターミナルへ分けます。API を止めずにラボやテストを実行するためです。」

- **本番と同じ操作でリハーサルする**

  **操作:** ブラウザーのチャット画面・VS Code の API ログ用ターミナル。下のブラウザー準備後、第 1 節と第 4 節の質問を送り、実回答と今回の MCP ログを確認する。モデル選択を変える場合は同じ確認を行う。VS Code のラボ・テスト用ターミナル。本編と同じ `events`、`tools`、読み取り専用 DB テストを一つずつ実行する。ラボの `Model:` 表示と結果を確認する

  **トーク:** 「ヘルスチェックだけでなく、実際の質問からデータ取得、回答表示までを確認します。候補に出るモデルでも、実行できるかは別に確かめます。本番と同じコマンドでリハーサルします。ブラウザーの選択モデルはラボには引き継がれないので、ラボ側のモデル名も確認します。」

- **予備の実行結果を記録する**

  **操作:** ブラウザーのチャット画面・VS Code のラボ・テスト用ターミナル。成功した結果のうち、機密情報のない回答・必要なログ行だけを Windows の画面切り取りで記録する。個人用の保存先を使い、リポジトリには追加しない

  **トーク:** 「通信が不安定な場合に備え、事前に成功した結果を記録します。本番で使う場合は、ライブ結果ではないことを明示します。」

**準備時の制約:** [pyproject.toml](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/pyproject.toml) の SDK は `1.0.9` 固定です。既存 DB を無断で消したり、使用中ポートの別プロセスを止めたりしません。モデルラボは通信障害の代替ではなく、事前記録かコード表示が代替です。`tools` サンプルの広い承認では、既定の公開サンプルの質問だけを使います。

### 開いておく画面とコード

- **チャット画面を準備する**

  **操作:** ブラウザー → ブラウザーのチャット画面。Edge/Chrome で `Ctrl+N` で新しいデモ用ウィンドウを開く。`Ctrl+L` → `http://localhost:5070/` → Enter。タイトルと入力欄が表示されることを確認

  **トーク:** 「最初のタブを、利用者が触るチャット画面にします。途中でここへ戻り、体験と実装を対応づけます。」

- **API 確認用の PowerShell を準備する**

  **操作:** VS Code の実行用 `LAB` ターミナルで `Get-Command Invoke-RestMethod` を入力して Enter。PowerShell のコマンドが見つかることを確認する。Bash を開いていた場合は、ターミナル右上の新規作成メニューから PowerShell を作り、`LAB` と改名する。取引・予測 API 用のブラウザータブは作らない。

  **トーク:** 「API の答え合わせも、この PowerShell で行います。取引一覧と予測を GET で取得して、必要な項目だけを読みやすく表示します。」

- **ローカルのシステムマップを準備する**

  **操作:** VS Code のコード画面 → ブラウザーのシステムマップ。VS Code のエクスプローラーで `docs` → `system-map` → `map.html` を右クリックし「パスのコピー」。ブラウザーで `Ctrl+T`、アドレスバーへ貼り付けて Enter。ブラウザーのシステムマップ。`Ctrl+L` → End、末尾に `#view=chat-request-path` を追記して Enter。経路図が表示されることを確認

  **トーク:** 「ブラウザーの二つ目のタブは、ローカルのシステムマップです。HTML を直接開くので、図の表示用サーバーは不要です。本編では URL の末尾を変え、チャット、MCP、REST の経路を順に見ます。」

- **ガバナンス資料を準備する**

  **操作:** ブラウザーのガバナンス資料。`Ctrl+T` を押し、冒頭の ブラウザーのガバナンス資料のリンク先 URL をアドレスバーへ貼り付けて開く。文書プレビューで `Ctrl+F` → `ライフサイクルイベント` → Enter、Esc

  **トーク:** 「ブラウザーの三つ目のタブは、フックの説明資料です。組織の管理画面や機密ログではなく、公開できる説明文を表示します。」

- **ローカル資料を予備にする場合**

  **操作:** GitHub のガバナンス資料が手元と異なる場合は、VS Code の `Ctrl+P` に `docs/breakouts/hooks-and-governance.md` を入力して Enter。`Ctrl+Shift+V` で Markdown プレビューを開き、「ライフサイクルイベント」までスクロールする。

  **トーク:** 「資料が手元と違う場合は、ローカルの Markdown プレビューを使います。同じライフサイクル表を見せるための予備です。」

- **タブとコードの表示を整える**

  **操作:** ブラウザーのタブを左から「Retail Analytics Assistant」「システムマップ」「ガバナンス資料」の三つに並べる。右上メニューのズームで文字を調整する。VS Code は下のソース索引からファイルを開いてタブを固定し、「表示」→「外観」→「拡大」でコードとターミナルを読みやすくする。

  **トーク:** 「タブの順番を固定し、画面切り替えのときに迷わないようにします。文字の大きさも投影に合わせます。コードのタブも準備します。全文を小さく見せるのではなく、説明する関数と数行を読める大きさで表示します。」

- **デモ用の表示履歴を消す**

  **操作:** ブラウザーのチャット画面。応答が完了してから `Clear` ボタンを一度クリックし、歓迎画面へ戻ったことを確認する。デモ専用の履歴に限る

  **トーク:** 「本編を最初の画面から始めるため、デモ用の表示履歴だけを消します。データベースを消す操作ではありません。」

- **画面共有の対象を確認する**

  **操作:** 発表者側。カンペは投影しない画面に置く。通知を無効にし、共有対象をデモのブラウザーと VS Code に限定する。個人ファイルや認証情報が映らないことを確認

  **トーク:** 「ここからデモ用の画面だけを共有します。認証情報や個人用の作業画面は共有しません。」

**ソース索引:** 以下は事前に開くための索引で、本編の追加操作ではありません。実際の移動とセリフは各節の箇条書きにあります。ファイルを探す場合の検索語も残しています。

- **1**: 最初に開くファイルと行: [app/services/copilot_chat.py:163](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L163)。その後の移動先・検索語: 182: 差分受信 / 132: `list_models` / 50: `_retail_mcp_config` / 79: `_permission_handler`
- **2**: 最初に開くファイルと行: [app/routers/chat.py:124](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/routers/chat.py#L124)。その後の移動先・検索語: 112: `stream_chat` / 85: `get_models`
- **3**: 最初に開くファイルと行: [app/static/app.js:170](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/static/app.js#L170)。その後の移動先・検索語: 178: `getReader` / 162: 描画タイマー / 113: `loadModels`
- **4**: 最初に開くファイルと行: [mcp_server/server.py:147](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L147)。その後の移動先・検索語: 152: `get_customer_summary` / 188: `predict_segment` / 57: `create_read_only_engine`
- **5**: 最初に開くファイルと行: [app/services/retail_analytics.py:83](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/retail_analytics.py#L83)。その後の移動先・検索語: 105: 高額購入の判定 / 125: `At Risk` の判定
- **6**: 最初に開くファイルと行: [.github/hooks/retail-governance.json:12](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.github/hooks/retail-governance.json#L12)。その後の移動先・検索語: 12: `preToolUse` / 20: `postToolUse`

40 分版で使うラボ・起動処理・テストの索引です。

- **2**: ファイルと行: [sdk_labs/events_sample.py:21](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/events_sample.py#L21)。見せるもの: イベントと差分件数
- **2**: ファイルと行: [sdk_labs/_common.py:16](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/_common.py#L16)。見せるもの: 完了・エラー・タイムアウト待ち
- **4**: ファイルと行: [sdk_labs/tools_sample.py:37](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/tools_sample.py#L37)。見せるもの: 引数スキーマと直接登録ツール
- **5**: ファイルと行: [app/main.py:28](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py#L28)。見せるもの: アプリのライフサイクル
- **7**: ファイルと行: [tests/test_mcp_server.py:158](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_mcp_server.py#L158)。見せるもの: 一時 DB を使う書き込み拒否テスト

**投影前チェック:** VS Code の `API` ターミナルは uvicorn が起動して INFO ログを表示し、PowerShell の `LAB` ターミナルは入力待ちであること。本編の GET コマンド二つも事前に実行し、取得と整形を確認します。ブラウザーのチャット画面は CDN の JavaScript を利用するため、会場ネットワークで描画と送信まで確認します。

### 数値の答え合わせ

次は**未変更のシードデータ**に対する期待値です。現在の DB を実測した結果ではありません。API の値が異なる場合は実データを優先します。金額データには通貨コードがないので、円への読み替えや換算はしません。

- **購入合計上位 3 件**: 確認する事実: `C003: 1,700.00`、`C005: 995.00`、`C001: 335.49`
- **`C002` の実績と予測**: 確認する事実: 2 件、合計 `47.50`、平均 `23.75`、`At Risk`
- **`C002` の `confidence`**: 確認する事実: `0.62` はルールに埋め込まれた値。検証された予測精度や確率とは説明しない

## 時間調整とトラブル時の進行

### 30 分・15 分への短縮

流れとコードの行番号は共通です。ラボを任意の補足として後から足すのではなく、40 分版では本編に含め、短縮するときに実演を減らします。

- **導入と完成形**: 40 分版: 6 分。30 分版: 4 分。15 分版: 2 分
- **ストリーミング**: 40 分版: 8 分。30 分版: 6 分。15 分版: 3 分
- **モデル選択**: 40 分版: 5 分。30 分版: 4 分。15 分版: 1 分
- **ツール呼び出し**: 40 分版: 9 分。30 分版: 7 分。15 分版: 3 分
- **アーキテクチャ**: 40 分版: 4 分。30 分版: 3 分。15 分版: 2 分
- **利用画面**: 40 分版: 2 分。30 分版: 1 分。15 分版: 1 分
- **ガバナンス**: 40 分版: 5 分。30 分版: 4 分。15 分版: 2 分
- **締め**: 40 分版: 1 分。30 分版: 1 分。15 分版: 1 分
- **合計**: 40 分版: **40 分**。30 分版: **30 分**。15 分版: **15 分**

**30 分版:** 問いかけは発表者がすぐ答える形にし、イベントラボは事前出力で説明、別モデルの比較は確認済みの結果、DB テストはコード表示に切り替えます。直接登録ツールの短い実演は残します。40 分の持ち枠で質疑を長めに取りたい場合は「本編 30 分 + 質疑 10 分」にします。

**15 分版:** イベントラボと直接登録ツールラボを省き、Web アプリのコードを中心に進めます。別モデルで再送せず設定経路だけを見せ、ターミナルでの取引照合、起動コード、DB テストの実行、問いかけも省きます。MCP の権限制御と DB の読み取り専用設定は残します。

短縮版でも、残す操作は本編の対応するセリフとセットで使います。省いたパートへの「次に実演します」という予告は読みません。

- **イベントラボを省略するとき**

  **操作:** VS Code のコード画面: ラボ省略。イベントラボを省く場合は、JavaScript の説明後、ブラウザーへ切り替え `Ctrl+1`

  **トーク:** 「イベント単体のラボは省略し、次は画面のモデル選択がどこへ渡るかを見ます。」

- **直接登録ツールを省略するとき**

  **操作:** VS Code のコード画面: 直接ツール省略。モデル説明後に `Ctrl+P` → `src/AgentOrchestrator-python/app/services/copilot_chat.py` → Enter、`Ctrl+G` → `69` → Enter

  **トーク:** 「最小の関数登録サンプルは省き、このアプリで実際に使っている MCP 接続を見ます。」

- **テスト実行を省略するとき**

  **操作:** VS Code の `Ctrl+P` に `src/AgentOrchestrator-python/tests/test_mcp_server.py` を入力して Enter、`Ctrl+G` → `158` → Enter。[tests/test_mcp_server.py:158～177](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/tests/test_mcp_server.py#L158-L177) を表示し、コマンドは実行しない。

  **トーク:** 「時間の都合でここでは実行せず、読み取りの成功と書き込み拒否を検証するテストのコードを示します。」

- **質疑応答へ移るとき**

  **操作:** ブラウザーのチャット画面: 質疑へ。30 分版の締め後、回答画面を表示したままにする

  **トーク:** 「本編はここまでです。残りの時間は、皆さんのアプリへ組み込む場合の疑問を伺います。」

### 10 分に短縮する場合

順番は変えず、導入と完成形 1 分半 → ストリーミング 2 分 → モデル選択 1 分 → ツール 2 分 → マップと利用画面 1 分半 → ガバナンスと締め 2 分とします。15 分版で省く項目に加え、JavaScript の詳細とフック JSON のコード表示も省きます。

### 止まったときの切り替え

- **本文が届くまで長く待っているとき**

  **操作:** ブラウザーのチャット画面: 待機が長い。30 秒ほど本文が出なければ VS Code へ切り替え、サービスの `Ctrl+G` → `163` → Enter。連打や追加送信はしない

  **トーク:** 「本文の到着に時間がかかっています。待つだけにせず、その間にセッションを作るコードを見ます。結果が届いたら画面へ戻ります。」

- **待機後に結果へ戻るとき**

  **操作:** VS Code のコード画面 → ブラウザーのチャット画面: 結果へ戻る。コード説明の区切りでブラウザーに戻り `Ctrl+1`。新しい本文があればその続き、完了済みなら最終回答を指す

  **トーク:** 「一度結果へ戻ります。いま届いている本文と、処理が終わっているかを確認します。」

- **モデルが使えないとき**

  **操作:** ブラウザーのチャット画面: モデル不調。応答終了後、右上のモデルを別の確認済み候補に変え、元の質問を一度だけ再送。終了していなければ再送せず事前記録へ進む

  **トーク:** 「このモデルでは回答を確認できないので、確認済みの候補で一度だけ試します。改善しなければ、事前の結果で接続の仕組みを説明します。」

- **回答が空のまま終わったとき**

  **操作:** VS Code の API ログ用ターミナル: UI が空で終了。`API` ターミナルを選び、直近の `Session error` または `Error during chat stream` を探す。秘密やプロンプト本文は拡大して見せない

  **トーク:** 「画面が空でも、API 側ではエラーになっている可能性があります。現在の UI はストリーム内の error を表示する分岐を持たないので、ログ側を確認します。」

- **DB が見つからないとき**

  **操作:** VS Code の API ログ用ターミナル: DB なし。`retail.db not found` の警告がある場合、その警告部分だけを指す。DB を削除・作り直す操作は本番で行わない

  **トーク:** 「この起動では DB を見つけられず、データ参照なしのチャットになっています。データ取得が成功したとは扱わず、設定コードへ切り替えます。」

- **API がエラーを返したとき**

  **操作:** VS Code の `LAB` ターミナルで `Invoke-RestMethod` のエラーを確認する。接続拒否・タイムアウトなら、ログ用 `API` ターミナルの uvicorn が起動中で、ポートが `5070` か確認する。HTTP エラーなら表示されたステータスを確認し、連続再試行せずコードの説明へ移る。エラーを実データとして扱わない。

  **トーク:** 「API の取得に失敗しているので、この結果では数値を照合できません。起動先を確認し、ここではコードで処理を説明します。」

- **C003 が見つからないとき**

  **操作:** VS Code の `LAB` ターミナルで、エラーがなくても取引の行が表示されなければ、実行した URL が `/api/transactions`、絞り込みが `C003` か確認する。現在の DB に該当データがない可能性があるため、初期値を実測結果として読み上げたり、DB を作り直したりしない。

  **トーク:** 「まず実行先を確認します。現在のデータには C003 を確認できないため、初期データの期待値を実測値として説明することは避けます。」

- **予測結果が想定と違うとき**

  **操作:** VS Code の `LAB` ターミナルに表示された `customerId` と、実行した URL の末尾の `C002` を照合する。入力を間違えた場合だけ、正しい URL で GET を再実行する。顧客 ID が正しければ、現在の DB の結果を優先する。

  **トーク:** 「指定した顧客と、実際の結果の顧客 ID を合わせます。正しい ID でも値が違う場合は、いまの DB の結果を優先します。」

- **PowerShell のコマンドが認識されないとき**

  **操作:** `Invoke-RestMethod` が認識されなければ、VS Code のターミナルで Bash を選んでいないか確認する。ターミナル右上の新規作成メニューから PowerShell を開き、該当節の GET コマンドをそのまま実行する。uvicorn のターミナルは止めない。

  **トーク:** 「このコマンドは PowerShell 用なので、実行するターミナルを合わせます。API やデータの変更ではありません。」

- **ターミナルの結果が読みにくいとき**

  **操作:** VS Code の下部パネルの上辺を上へドラッグして広げ、「表示」→「外観」→「拡大」で文字を調整する。取引は `Format-Table`、予測は `Format-List` まで含めた本編のコマンドを使う。過去の出力に埋もれた場合は今回のコマンドの直下へスクロールする。

  **トーク:** 「結果を読みやすく表示します。生の JSON を探すのではなく、取引は顧客と金額の列、予測は判定と根拠の一覧にしています。」

- **ラボが終了しないとき**

  **操作:** VS Code のラボ・テスト用ターミナル: ラボ継続中。`LAB` をクリックして `Ctrl+C` を一度押す。プロンプトが戻るまで次のコマンドを入力しない。戻らなければそのターミナルを再利用せず、以降はコードと事前記録を使う

  **トーク:** 「ラボが完了しないため、このコマンドを中断します。API のターミナルは止めず、残りはコードと事前記録で進めます。」

- **事前の記録へ切り替えるとき**

  **操作:** 事前記録。認証・通信・表示の障害時は、Windows のエクスプローラーでリハーサル記録を保存したフォルダーを開き、該当スクリーンショットをダブルクリック。画像ビューアーの最大化ボタンを押す

  **トーク:** 「ここからは、リハーサルで取得した結果です。現在のライブ実行の結果ではありません。注目してほしい箇所を、この記録で説明します。」

- **事前の記録がないとき**

  **操作:** 記録を探し続けず、VS Code で [app/services/copilot_chat.py:163～173](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L163-L173) のセッション設定、[同ファイルの69～76行](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L69-L76) の MCP 起動設定、[mcp_server/server.py:147～158](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L147-L158) の顧客取得関数を順に開く。各ファイルへは `Ctrl+P`、記載行へは `Ctrl+G` で移動する。

  **トーク:** 「事前の記録もないため、実行結果の説明はせず、コードで確認できる接続と処理の範囲に絞ります。」

- **権限拒否を実証できないとき**

  **操作:** VS Code で [app/services/copilot_chat.py:89～104](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L89-L104) の権限ハンドラー、続いて [mcp_server/server.py:57～71](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L57-L71) の DB 接続を表示する。`Ctrl+P` でファイル、`Ctrl+G` で行を指定する。危険なコマンドを即興で試さない。

  **トーク:** 「拒否の実動作を確認できていないので、ここでは判定条件と DB 接続設定を見せます。安全性を全面的に実証したとは説明しません。」

- **システムマップが表示されないとき**

  **操作:** マップが表示できなければ VS Code へ切り替え、[app/main.py:28～41](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/main.py#L28-L41)、[app/services/copilot_chat.py:163～173](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/app/services/copilot_chat.py#L163-L173)、[mcp_server/server.py:183～193](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/mcp_server/server.py#L183-L193) を順に表示する。Python アプリの起動、SDK セッション、業務ツールへの接続の順に指す。

  **トーク:** 「図の表示が使えないため、起動コード、SDK サービス、MCP サーバーの順で、同じ役割分担を説明します。」

- **コードの行番号がずれているとき**

  **操作:** VS Code のコード画面: 行番号ずれ。対象ファイル内で `Ctrl+F` に本編の関数名または固有のコードを入力し、Enter。該当箇所で Esc

  **トーク:** 「手元の変更で行番号がずれているので、関数名で該当箇所へ移ります。見るポイントは同じです。」

**記録について:** 既存の[UI スクリーンショット](04-web-ui.md)の一般的な KPI 回答は、今回の MCP データ参照成功の証拠には使いません。数値照合には該当の質問・データ・実行結果を記録したものが必要です。保存先は投影前に決め、認証情報や個人ファイルのあるフォルダーは画面共有しません。

## 発表者向け検証メモ

**確認日:** 2026-09-14。基準コミットは `e3f2add`、確認対象は未コミットの変更も含む作業ツリー上の Python 実装（SDK `1.0.9` 固定）と両トラックのデモ資料です。以下はコードと公式文書の照合結果であり、認証を伴うライブ動作の検証結果ではありません。

**ドキュメント検査:** ソースリンクの欠落は 0 件、既存 Mermaid 図は 4 件すべて描画成功。サイトの厳格ビルドは、依存パッケージ取得先との TLS 接続エラーにより未完了です。

**2026-09-15 の追加確認:** 本編の PowerShell GET コマンド二つを、起動済みのローカル API に対して実行しました。C003 の取引は `1250.00` と `450.00`、C002 の予測は `At Risk`、`confidence: 0.62` と表示されました。これは REST API の取得・整形の確認であり、認証を伴う LLM 応答の再検証ではありません。

- **Copilot SDK の提供段階**: 状態: 変更あり。本番での扱い: 現在の公式 README は GA と明記。古い資料の Technical Preview を引用しない
- **差分イベントによるストリーミング**: 状態: 公式仕様・コードで確認。本番での扱い: `streaming=True`、イベント購読、SSE への変換を示す
- **モデル検出・選択**: 状態: 公式仕様・コードで確認。本番での扱い: モデルの利用権限や当日の可用性は、実際の応答で別途確認
- **カスタムツール・MCP 接続**: 状態: 公式仕様・コードで確認。本番での扱い: 直接登録のラボと、Web アプリの MCP 経路を区別する
- **権限ハンドラーと DB 読み取り専用**: 状態: コードで確認、実行環境依存部分あり。本番での扱い: このハンドラーの条件と MCP 接続の保証範囲を説明。全面的な隔離と表現しない
- **SDK セッションフック**: 状態: 公式仕様で確認、チャットでの明示登録なし。本番での扱い: 運用への拡張点として示す。CLI のリポジトリフックとは設定経路を区別
- **会話継続・組織監査への連携**: 状態: このチャットでは未実証。本番での扱い: UI 履歴やローカルログから実装済みと推測しない

今回使う中核機能について、廃止との記載は確認していません。ただし公式 `main` の API 例とこのリポジトリの固定版は一致するとは限りません。たとえば、現在の公式 Python README では「権限ハンドラー省略時はイベント経由で手動解決待ち」と説明されており、古い資料の「省略すると常に拒否」を一般仕様として断言しません。MCP 設定も、この実装の `working_directory` を基準に見せ、別版の例を本番直前に貼り替えません。

公式情報の参照先:

- [Copilot SDK README: 提供段階・構成・モデル・認証](https://github.com/github/copilot-sdk)
- [Python SDK: Streaming / Tools / Permission Handling / Session Hooks](https://github.com/github/copilot-sdk/blob/main/python/README.md)
- [MCP サーバーの接続](https://github.com/github/copilot-sdk/blob/main/docs/features/mcp.md)
- [SDK セッションフック](https://github.com/github/copilot-sdk/blob/main/docs/features/hooks.md)

既存の[アーキテクチャ解説](../breakouts/architecture.md)は主に .NET のコードとポートで説明しているため、今回の本編には両トラック対応の[システムマップ](../system-map/)を使います。意図的なコードスメルは別のコードレビューデモ用なので、本編では修正しません。