# メッセージングとワーカー処理

このアプリの「非同期実行」は Redis Pub/Sub を中心に動きます。API とワーカーは別プロセスで動き、イベントを介して連携します。

## Redis Pub/Sub の役割

- **イベントの配信路**: `job_events` チャンネル
- **発行者**: API（ユースケース経由）
- **購読者**: ワーカー / SSE

実装位置:
- チャンネル定義: `adapters/outbound/messaging/redis_event_publisher.py`
- 配信: `RedisEventPublisher.publish()`
- 購読（SSE）: `adapters/inbound/sse/job_sse.py`
- 購読（Worker）: `worker.py`

## ワーカーの役割

ワーカーは「ジョブ作成イベントを受けて実行し、状態を更新する」独立プロセスです。

### 処理フロー（要約）

1. Redis の `job_events` を Subscribe
2. `JobCreated` を受信
3. ジョブを取得し `start()` で RUNNING にする
4. ダミージョブを実行（sleep）
5. 完了したら `complete()` で COMPLETED にする
6. 途中でキャンセルされていたら停止
7. 失敗時は `fail()` で FAILED にする

### 実装位置

- `backend/src/app/worker.py`

## SSE（リアルタイム更新）との関係

フロントエンドは SSE でリアルタイム更新を受け取ります。

- ワーカーが更新 → イベントを Redis へ Publish
- SSE が Redis を Subscribe
- SSE がブラウザへストリーム配信

この構造により、**API サーバーに負荷をかけずにリアルタイム更新**が可能です。
