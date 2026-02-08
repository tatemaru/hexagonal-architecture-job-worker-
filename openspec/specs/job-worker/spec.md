## ADDED Requirements

### Requirement: ワーカープロセスによるジョブ実行

ワーカーは API サーバーとは独立したプロセスとして動作しなければならない（SHALL）。Redis Pub/Sub の `job_events` チャンネルを Subscribe し、JobCreated イベントを受信してジョブを実行する。

#### Scenario: JobCreated イベントの受信と実行開始
- **WHEN** ワーカーが Redis Pub/Sub から JobCreated イベントを受信する
- **THEN** 該当ジョブを Repository から取得し、start() で RUNNING に遷移させ、JobStarted イベントを Publish する

#### Scenario: ジョブの正常完了
- **WHEN** ダミージョブ（指定秒数の sleep）が正常に終了する
- **THEN** Job 集約の complete() を呼び出し、ステータスを COMPLETED に遷移させ、JobCompleted イベントを Publish する

#### Scenario: ジョブの実行失敗
- **WHEN** ジョブの実行中に予期しないエラーが発生する
- **THEN** Job 集約の fail() を呼び出し、ステータスを FAILED に遷移させ、エラー情報を JobResult に記録し、JobFailed イベントを Publish する

### Requirement: 実行中ジョブのキャンセル検知

ワーカーはダミージョブの実行中（sleep 中）に1秒間隔でキャンセルフラグをポーリングしなければならない（SHALL）。キャンセルが検知された場合、実行を中断する。

#### Scenario: 実行中にキャンセルを検知
- **WHEN** ワーカーがポーリングで Job のステータスが CANCELLED に変わったことを検知する
- **THEN** sleep ループを中断し、ジョブの実行を終了する

#### Scenario: キャンセルされていない場合の継続
- **WHEN** ワーカーがポーリングで Job のステータスが RUNNING のままである
- **THEN** sleep ループを継続する

### Requirement: ドメインモデルの共有

ワーカーは API サーバーと同じ Python コードベース（ドメイン層・ポート層・アダプター層）を共有しなければならない（SHALL）。エントリーポイントのみが異なる。

#### Scenario: ワーカーの起動
- **WHEN** `python -m app.worker` が実行される
- **THEN** ワーカープロセスが起動し、Redis Pub/Sub の Subscribe を開始する
