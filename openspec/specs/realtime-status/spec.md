## ADDED Requirements

### Requirement: SSE によるリアルタイム状態通知

システムは SSE（Server-Sent Events）エンドポイントを提供し、ドメインイベントをリアルタイムでクライアントに配信しなければならない（SHALL）。API サーバーが Redis Pub/Sub の `job_events` チャンネルを Subscribe し、受信したイベントを SSE ストリームに変換する。

#### Scenario: SSE 接続の確立
- **WHEN** クライアントが `GET /api/jobs/stream` にリクエストする
- **THEN** `Content-Type: text/event-stream` のレスポンスが返され、接続が維持される

#### Scenario: ドメインイベントの SSE 配信
- **WHEN** Redis Pub/Sub から JobStarted イベントを受信する
- **THEN** SSE ストリームに `event: JobStarted` とイベントデータ（JSON）が送信される

#### Scenario: 複数クライアントへの同時配信
- **WHEN** 複数のクライアントが SSE エンドポイントに接続している状態でドメインイベントが発生する
- **THEN** 接続中の全クライアントにイベントが配信される

### Requirement: SSE イベントのデータ形式

SSE で配信されるイベントは以下の形式でなければならない（SHALL）。

```
event: <イベント種別>
data: {"job_id": "<uuid>", "status": "<ステータス>", "timestamp": "<ISO8601>"}
```

#### Scenario: JobCompleted イベントの SSE 形式
- **WHEN** JobCompleted ドメインイベントが SSE で配信される
- **THEN** `event: JobCompleted` ヘッダーと、job_id・status・timestamp を含む JSON データが送信される

### Requirement: SSE 接続の切断処理

クライアントが SSE 接続を切断した場合、サーバーはリソースを適切にクリーンアップしなければならない（SHALL）。

#### Scenario: クライアントの切断
- **WHEN** クライアントが SSE 接続を閉じる（ブラウザタブを閉じるなど）
- **THEN** サーバー側の該当クライアント向け処理が終了し、メモリリークが発生しない
