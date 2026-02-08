## 1. ドメイン層の変更

- [x] 1.1 `NotificationChannel` Enum（NONE / EMAIL / DISCORD）を `domain/models/job.py` に追加する
- [x] 1.2 `Job` aggregate に `notification_channel: NotificationChannel` フィールドを追加する（デフォルト: NONE）
- [x] 1.3 `Job.create()` ファクトリメソッドに `notification_channel` 引数を追加する

## 2. ポート層の変更

- [x] 2.1 `ports/notification_sender.py` に `NotificationSender` 抽象基底クラスを定義する（`send(job: Job) -> None`）

## 3. アダプター層の変更

- [x] 3.1 `adapters/outbound/notification/email_notification_sender.py` に `EmailNotificationSender` を実装する（aiosmtplib 使用）
- [x] 3.2 `adapters/outbound/notification/discord_notification_sender.py` に `DiscordNotificationSender` を実装する（httpx 使用）
- [x] 3.3 `adapters/outbound/notification/null_notification_sender.py` に `NullNotificationSender` を実装する
- [x] 3.4 `adapters/outbound/notification/notification_sender_factory.py` に `NotificationSenderFactory` を実装する

## 4. 永続化層の変更

- [x] 4.1 `adapters/outbound/persistence/models.py` の `JobRow` に `notification_channel` カラム（String, デフォルト "NONE"）を追加する
- [x] 4.2 `PostgresJobRepository` のドメインモデル ↔ ORM モデル変換に `notification_channel` を追加する

## 5. ユースケース層の変更

- [x] 5.1 `CreateJobUseCase.execute()` に `notification_channel` 引数を追加する

## 6. API 層の変更

- [x] 6.1 `POST /api/jobs` のリクエストスキーマに `notification_channel`（オプション、デフォルト "none"）を追加する
- [x] 6.2 ジョブのレスポンススキーマに `notification_channel` フィールドを追加する

## 7. ワーカーの変更

- [x] 7.1 `worker.py` に `NotificationSenderFactory` を組み込み、ジョブ完了後に通知を送信する
- [x] 7.2 `worker.py` のジョブ失敗後に通知を送信する処理を追加する
- [x] 7.3 通知送信を try-except で囲み、失敗時はログ出力のみにする

## 8. フロントエンドの変更

- [x] 8.1 `jobApi.ts` の createJob に `notification_channel` パラメータを追加する
- [x] 8.2 `JobCreateForm.tsx` に通知チャネル選択のセレクトボックスを追加する（なし / Email / Discord）
- [x] 8.3 `JobList.tsx` のテーブルに通知チャネル列を追加する

## 9. インフラの変更

- [x] 9.1 `docker-compose.yml` に MailPit コンテナを追加する（SMTP: 1025、Web UI: 8025）
- [x] 9.2 `docker-compose.yml` の worker サービスに通知関連の環境変数を追加する（SMTP_HOST, SMTP_PORT, NOTIFICATION_EMAIL_FROM, NOTIFICATION_EMAIL_TO, DISCORD_WEBHOOK_URL）
- [x] 9.3 backend の依存関係に `aiosmtplib` と `httpx` を追加する
