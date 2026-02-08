## ADDED Requirements

### Requirement: ジョブ作成フォーム

フロントエンドはジョブを作成するためのフォームを提供しなければならない（SHALL）。ユーザーは実行秒数を入力し、通知チャネル（なし / Email / Discord）を選択してジョブを作成できる。

#### Scenario: ジョブの作成
- **WHEN** ユーザーが実行秒数を入力し「作成」ボタンを押す
- **THEN** `POST /api/jobs` が選択された notification_channel を含めて呼び出され、ジョブ一覧に新しいジョブが PENDING 状態で表示される

#### Scenario: 通知チャネルの選択
- **WHEN** ユーザーがジョブ作成フォームを表示する
- **THEN** 通知チャネルを選択するセレクトボックスが表示され、「なし」「Email」「Discord」の選択肢がある

#### Scenario: 通知チャネルのデフォルト値
- **WHEN** ユーザーがジョブ作成フォームを初期表示する
- **THEN** 通知チャネルのデフォルト値は「なし」（none）である

#### Scenario: 入力バリデーション
- **WHEN** ユーザーが実行秒数を入力せずに「作成」ボタンを押す
- **THEN** エラーメッセージが表示され、API は呼び出されない

### Requirement: ジョブ一覧テーブル

フロントエンドはジョブの一覧をテーブル形式で表示しなければならない（SHALL）。各行にはジョブ ID、ステータス、種別、通知チャネル、作成日時、操作ボタンが含まれる。

#### Scenario: ジョブ一覧の表示
- **WHEN** ユーザーが画面を開く
- **THEN** `GET /api/jobs` が呼び出され、ジョブ一覧がテーブルで表示され、各行に通知チャネルが表示される

#### Scenario: キャンセルボタンの表示
- **WHEN** ジョブのステータスが PENDING または RUNNING である
- **THEN** 該当行に「キャンセル」ボタンが表示される

#### Scenario: キャンセルボタンの非表示
- **WHEN** ジョブのステータスが COMPLETED、FAILED、または CANCELLED である
- **THEN** 該当行に「キャンセル」ボタンは表示されない

### Requirement: ジョブのキャンセル操作

フロントエンドからジョブをキャンセルできなければならない（SHALL）。

#### Scenario: キャンセル操作の実行
- **WHEN** ユーザーがジョブ一覧の「キャンセル」ボタンを押す
- **THEN** `POST /api/jobs/{job_id}/cancel` が呼び出され、該当ジョブのステータスが CANCELLED に更新される

### Requirement: リアルタイムステータス更新

フロントエンドは SSE を通じてジョブのステータスをリアルタイムに更新しなければならない（SHALL）。ページのリロードなしでステータスが反映される。

#### Scenario: SSE によるステータス更新
- **WHEN** SSE で JobStarted イベントを受信する
- **THEN** 該当ジョブのステータス表示が手動操作なしで RUNNING に更新される

#### Scenario: SSE 接続の自動確立
- **WHEN** ユーザーが画面を開く
- **THEN** `GET /api/jobs/stream` への SSE 接続が自動的に確立される

### Requirement: ステータスバッジの視覚的区別

各ステータスは色分けされたバッジで表示しなければならない（SHALL）。ユーザーがジョブの状態を一目で識別できるようにする。

#### Scenario: ステータスごとの色分け
- **WHEN** ジョブ一覧が表示される
- **THEN** PENDING は灰色、RUNNING は青色、COMPLETED は緑色、FAILED は赤色、CANCELLED は黄色のバッジで表示される
