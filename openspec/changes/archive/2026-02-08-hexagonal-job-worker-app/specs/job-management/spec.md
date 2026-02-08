## ADDED Requirements

### Requirement: Job 集約によるライフサイクル管理

システムは Job 集約ルートを通じてのみジョブの状態を変更しなければならない（SHALL）。Job 集約は JobId（UUID）、JobStatus、JobType、JobResult の値オブジェクトを保持し、ステートマシンで定義された状態遷移ルールを内部で強制する。

#### Scenario: 許可された状態遷移が成功する
- **WHEN** Job の現在のステータスが PENDING であり、start() が呼ばれる
- **THEN** ステータスが RUNNING に遷移し、JobStarted ドメインイベントが発行される

#### Scenario: 禁止された状態遷移が拒否される
- **WHEN** Job の現在のステータスが COMPLETED であり、cancel() が呼ばれる
- **THEN** ドメイン例外が発生し、ステータスは COMPLETED のまま変更されない

### Requirement: ジョブの作成

システムはユーザーからのリクエストに基づき新しいジョブを作成できなければならない（SHALL）。ジョブ作成時には JobType（ダミージョブの実行秒数）を指定する。作成されたジョブは PENDING 状態で保存され、JobCreated ドメインイベントが発行される。

#### Scenario: ジョブの新規作成
- **WHEN** ユーザーが実行秒数を指定してジョブ作成をリクエストする
- **THEN** PENDING 状態のジョブが永続化され、JobCreated イベントが Redis Pub/Sub に配信される

### Requirement: ジョブの一覧取得

システムは保存されているジョブの一覧を取得できなければならない（SHALL）。一覧には各ジョブの ID、ステータス、種別、作成日時が含まれる。

#### Scenario: ジョブ一覧の取得
- **WHEN** ユーザーがジョブ一覧を要求する
- **THEN** 全ジョブが作成日時の降順で返される

### Requirement: ジョブの詳細取得

システムは指定された JobId のジョブ詳細を取得できなければならない（SHALL）。詳細には ID、ステータス、種別、作成日時、開始日時、完了日時、実行結果が含まれる。

#### Scenario: 存在するジョブの詳細取得
- **WHEN** ユーザーが存在する JobId を指定してジョブ詳細を要求する
- **THEN** 該当ジョブの全情報が返される

#### Scenario: 存在しないジョブの詳細取得
- **WHEN** ユーザーが存在しない JobId を指定してジョブ詳細を要求する
- **THEN** ジョブが見つからないエラーが返される

### Requirement: ジョブのキャンセル

システムは PENDING または RUNNING 状態のジョブをキャンセルできなければならない（SHALL）。キャンセルが成功すると JobCancelled ドメインイベントが発行される。

#### Scenario: PENDING 状態のジョブをキャンセル
- **WHEN** ユーザーが PENDING 状態のジョブに対してキャンセルを要求する
- **THEN** ステータスが CANCELLED に遷移し、JobCancelled イベントが配信される

#### Scenario: RUNNING 状態のジョブをキャンセル
- **WHEN** ユーザーが RUNNING 状態のジョブに対してキャンセルを要求する
- **THEN** ステータスが CANCELLED に遷移し、ワーカーが次回のポーリング時に実行を中断する

#### Scenario: 完了済みジョブのキャンセル拒否
- **WHEN** ユーザーが COMPLETED または FAILED 状態のジョブに対してキャンセルを要求する
- **THEN** ドメイン例外が発生し、ステータスは変更されない

### Requirement: REST API エンドポイント

システムは以下の REST API エンドポイントを提供しなければならない（SHALL）。

| メソッド | パス | 説明 |
|---|---|---|
| POST | /api/jobs | ジョブの作成 |
| GET | /api/jobs | ジョブ一覧の取得 |
| GET | /api/jobs/{job_id} | ジョブ詳細の取得 |
| POST | /api/jobs/{job_id}/cancel | ジョブのキャンセル |

#### Scenario: POST /api/jobs でジョブ作成
- **WHEN** クライアントが `POST /api/jobs` に `{"duration_seconds": 10}` を送信する
- **THEN** 201 レスポンスで作成されたジョブの情報が返される

#### Scenario: GET /api/jobs でジョブ一覧取得
- **WHEN** クライアントが `GET /api/jobs` にリクエストする
- **THEN** 200 レスポンスでジョブの配列が返される

#### Scenario: GET /api/jobs/{job_id} でジョブ詳細取得
- **WHEN** クライアントが存在する job_id で `GET /api/jobs/{job_id}` にリクエストする
- **THEN** 200 レスポンスでジョブの詳細情報が返される

#### Scenario: POST /api/jobs/{job_id}/cancel でキャンセル
- **WHEN** クライアントが PENDING 状態のジョブに対して `POST /api/jobs/{job_id}/cancel` を送信する
- **THEN** 200 レスポンスでキャンセル済みのジョブ情報が返される
