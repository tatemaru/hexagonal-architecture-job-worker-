# このアプリのディレクトリ構成とレイヤー対応

バックエンドの中心は `backend/src/app` です。以下はディレクトリ構成と役割の対応表です。

## レイヤー対応表

| レイヤー | 役割 | 対応ディレクトリ/ファイル |
| --- | --- | --- |
| ドメイン | ルールと不変条件 | `backend/src/app/domain/**` |
| ユースケース | アプリの操作単位 | `backend/src/app/usecases/**` |
| ポート | 抽象インターフェース | `backend/src/app/ports/**` |
| プライマリアダプター | 入力（HTTP/SSE） | `backend/src/app/adapters/inbound/**` |
| セカンダリアダプター | 出力（DB/Redis/通知） | `backend/src/app/adapters/outbound/**` |
| エントリポイント | 起動と組み立て | `backend/src/app/main.py`, `backend/src/app/worker.py` |

## 実際のコード配置例

### ドメイン

- `backend/src/app/domain/models/job.py`
- `backend/src/app/domain/models/notification.py`
- `backend/src/app/domain/events/job_events.py`

### ユースケース

- `backend/src/app/usecases/create_job.py`
- `backend/src/app/usecases/cancel_job.py`
- `backend/src/app/usecases/get_job.py`
- `backend/src/app/usecases/list_jobs.py`

### ポート

- `backend/src/app/ports/repository.py`
- `backend/src/app/ports/event_publisher.py`
- `backend/src/app/ports/notification_sender.py`

### アダプター（入力）

- REST: `backend/src/app/adapters/inbound/api/job_router.py`
- SSE: `backend/src/app/adapters/inbound/sse/job_sse.py`

### アダプター（出力）

- DB: `backend/src/app/adapters/outbound/persistence/postgres_job_repository.py`
- Redis: `backend/src/app/adapters/outbound/messaging/redis_event_publisher.py`
- 通知: `backend/src/app/adapters/outbound/notification/*`

## 依存関係のルール（意識する順番）

- ドメインは **何にも依存しない**
- ユースケースは **ドメインとポートに依存**
- アダプターは **ポートと外部技術に依存**

この依存関係が崩れると、変更に弱い構造になります。
