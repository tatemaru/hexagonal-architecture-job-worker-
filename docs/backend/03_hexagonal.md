# ヘキサゴナルアーキテクチャを厚めに理解する

ヘキサゴナルアーキテクチャ（Ports and Adapters）は「中心のルール（ドメイン）を、外部技術から守る」ための設計です。重要なのは **“中心は外部に依存しない”** という一点です。

## なぜ必要か

外部技術（DB/HTTP/メッセージング）は変わりやすい一方、業務ルールは変わりにくい。
ヘキサゴナルは以下を狙います。

- ドメインやユースケースが **DB/HTTP/Redis に引きずられない**
- 外部技術の差し替えが **局所変更** で済む
- テストが **単体でやりやすい**

## 中心と周辺

中心: **ドメイン + ユースケース**
周辺: **アダプター（HTTP、DB、Redis、通知など）**

中心は「やりたいこと（ルール）」、周辺は「どう繋ぐか（技術）」を担当します。

## ポートとアダプターの関係

- **ポート（Port）**: 中心が「外の何か」に期待する抽象インターフェース
- **アダプター（Adapter）**: 具体技術を使ってポートを実装するもの

ポートは中心側に置き、アダプターは外側に置きます。これが依存性逆転のポイントです。

## プライマリ / セカンダリ

- **プライマリアダプター（入力側）**: 外部から中心へ入ってくる
  - 例: REST API, SSE
- **セカンダリアダプター（出力側）**: 中心から外部へ出ていく
  - 例: DB, Redis, 通知（Email/Discord）

## このアプリでの具体的対応

### 中心（ドメイン/ユースケース）

- ドメイン: `backend/src/app/domain/**`
  - `Job` 集約、`JobStatus` 状態遷移、ドメインイベント
- ユースケース: `backend/src/app/usecases/**`
  - `CreateJobUseCase`, `CancelJobUseCase` など

### ポート（抽象インターフェース）

- `backend/src/app/ports/repository.py` (JobRepository)
- `backend/src/app/ports/event_publisher.py` (EventPublisher)
- `backend/src/app/ports/notification_sender.py` (NotificationSender)

### プライマリアダプター（入力側）

- REST API: `backend/src/app/adapters/inbound/api/job_router.py`
- SSE: `backend/src/app/adapters/inbound/sse/job_sse.py`

### セカンダリアダプター（出力側）

- DB: `backend/src/app/adapters/outbound/persistence/postgres_job_repository.py`
- Redis Pub/Sub: `backend/src/app/adapters/outbound/messaging/redis_event_publisher.py`
- 通知: `backend/src/app/adapters/outbound/notification/*`

## 図で見る関係（概念）

```
[API/SSE] ---> [UseCases] ---> [Domain]
                 |   ^
                 v   |
            [Ports (抽象)]
                 |   ^
                 v   |
        [Adapters: DB/Redis/Notify]
```

- 左が入力側（プライマリ）
- 右が出力側（セカンダリ）
- 中心はポートにしか依存しない

## 実装読みのポイント

- **外から中心へ**: API → UseCase → Domain
- **中心から外へ**: Domain events → Publisher → Redis → Worker/SSE

「どこが中心で、どこが外側か」を意識するだけで、コードの見通しが大きく改善します。
