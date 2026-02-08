## MODIFIED Requirements

### Requirement: ジョブの作成

システムはユーザーからのリクエストに基づき新しいジョブを作成できなければならない（SHALL）。ジョブ作成時には JobType（ダミージョブの実行秒数）と NotificationChannel（通知チャネル: NONE / EMAIL / DISCORD）を指定する。作成されたジョブは PENDING 状態で保存され、JobCreated ドメインイベントが発行される。NotificationChannel が省略された場合は NONE がデフォルトとなる。

#### Scenario: ジョブの新規作成
- **WHEN** ユーザーが実行秒数を指定してジョブ作成をリクエストする
- **THEN** PENDING 状態のジョブが永続化され、JobCreated イベントが Redis Pub/Sub に配信される

#### Scenario: 通知チャネル付きでジョブを作成
- **WHEN** ユーザーが実行秒数と notification_channel に "email" を指定してジョブ作成をリクエストする
- **THEN** notification_channel が EMAIL に設定された PENDING 状態のジョブが永続化される

#### Scenario: 通知チャネル省略時のデフォルト
- **WHEN** ユーザーが notification_channel を指定せずにジョブ作成をリクエストする
- **THEN** notification_channel が NONE に設定されたジョブが作成される

### Requirement: Job 集約によるライフサイクル管理

システムは Job 集約ルートを通じてのみジョブの状態を変更しなければならない（SHALL）。Job 集約は JobId（UUID）、JobStatus、JobType、JobResult、NotificationChannel の値オブジェクトを保持し、ステートマシンで定義された状態遷移ルールを内部で強制する。

#### Scenario: 許可された状態遷移が成功する
- **WHEN** Job の現在のステータスが PENDING であり、start() が呼ばれる
- **THEN** ステータスが RUNNING に遷移し、JobStarted ドメインイベントが発行される

#### Scenario: 禁止された状態遷移が拒否される
- **WHEN** Job の現在のステータスが COMPLETED であり、cancel() が呼ばれる
- **THEN** ドメイン例外が発生し、ステータスは COMPLETED のまま変更されない

### Requirement: REST API エンドポイント

システムは以下の REST API エンドポイントを提供しなければならない（SHALL）。

| メソッド | パス | 説明 |
|---|---|---|
| POST | /api/jobs | ジョブの作成 |
| GET | /api/jobs | ジョブ一覧の取得 |
| GET | /api/jobs/{job_id} | ジョブ詳細の取得 |
| POST | /api/jobs/{job_id}/cancel | ジョブのキャンセル |

#### Scenario: POST /api/jobs でジョブ作成
- **WHEN** クライアントが `POST /api/jobs` に `{"duration_seconds": 10, "notification_channel": "email"}` を送信する
- **THEN** 201 レスポンスで作成されたジョブの情報（notification_channel を含む）が返される

#### Scenario: POST /api/jobs で通知チャネル省略
- **WHEN** クライアントが `POST /api/jobs` に `{"duration_seconds": 10}` を送信する（notification_channel 省略）
- **THEN** 201 レスポンスで notification_channel が "none" のジョブが返される

#### Scenario: GET /api/jobs でジョブ一覧取得
- **WHEN** クライアントが `GET /api/jobs` にリクエストする
- **THEN** 200 レスポンスでジョブの配列が返され、各ジョブに notification_channel が含まれる

#### Scenario: GET /api/jobs/{job_id} でジョブ詳細取得
- **WHEN** クライアントが存在する job_id で `GET /api/jobs/{job_id}` にリクエストする
- **THEN** 200 レスポンスでジョブの詳細情報（notification_channel を含む）が返される

#### Scenario: POST /api/jobs/{job_id}/cancel でキャンセル
- **WHEN** クライアントが PENDING 状態のジョブに対して `POST /api/jobs/{job_id}/cancel` を送信する
- **THEN** 200 レスポンスでキャンセル済みのジョブ情報が返される
