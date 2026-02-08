# 読みどころ（コードパスの案内）

この章は「どこから読むと迷わないか」を示すガイドです。実装理解のために、下記の順で開いてください。

## 入口から読む

1. `backend/src/app/main.py`
   - FastAPI 起動時の初期化（DB/Redis）
   - ルーター登録順の注意点

2. `backend/src/app/adapters/inbound/api/job_router.py`
   - API エンドポイントの定義
   - どのユースケースが呼ばれているかが分かる

3. `backend/src/app/usecases/*`
   - 1 ユースケース = 1 意図
   - ドメインとポートの使い方が見える

4. `backend/src/app/domain/models/job.py`
   - 状態遷移ルール（ルールの中心）
   - ドメインイベントの発行

## 非同期フローを読む

5. `backend/src/app/adapters/outbound/messaging/redis_event_publisher.py`
   - ドメインイベントが Redis に流れる

6. `backend/src/app/worker.py`
   - Pub/Sub を受信しジョブを実行
   - 実行完了/失敗の通知

7. `backend/src/app/adapters/inbound/sse/job_sse.py`
   - イベントをブラウザにリアルタイム配信

## データモデルを読む

8. `backend/src/app/adapters/outbound/persistence/models.py`
9. `backend/src/app/adapters/outbound/persistence/postgres_job_repository.py`

## 変更時のヒント

- ルール変更 → `domain/models/job.py`
- API 追加/変更 → `adapters/inbound/api/job_router.py`
- DB 変更 → `adapters/outbound/persistence/*`
- 通知追加 → `adapters/outbound/notification/*`
