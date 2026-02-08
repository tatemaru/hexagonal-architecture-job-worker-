## ADDED Requirements

### Requirement: NotificationSender ポート

システムは通知送信のための抽象ポート `NotificationSender` を定義しなければならない（SHALL）。このポートは `send(job: Job) -> None` メソッドを持ち、Email・Discord の各アダプターがこれを実装する。

#### Scenario: ポートを通じた通知送信
- **WHEN** ワーカーが NotificationSender の send メソッドを呼び出す
- **THEN** 具体的なアダプター実装に委譲され、通知が送信される

### Requirement: Email 通知アダプター

システムは SMTP 経由で Email 通知を送信する `EmailNotificationSender` アダプターを提供しなければならない（SHALL）。SMTP 接続設定（ホスト、ポート）と宛先メールアドレスは環境変数から取得する。

#### Scenario: ジョブ完了時の Email 通知
- **WHEN** ジョブが COMPLETED 状態に遷移し、notification_channel が EMAIL である
- **THEN** ジョブ ID とステータスを含む Email が環境変数 `NOTIFICATION_EMAIL_TO` の宛先に送信される

#### Scenario: ジョブ失敗時の Email 通知
- **WHEN** ジョブが FAILED 状態に遷移し、notification_channel が EMAIL である
- **THEN** ジョブ ID、ステータス、エラー情報を含む Email が送信される

#### Scenario: SMTP 接続失敗時のフォールバック
- **WHEN** SMTP サーバーへの接続に失敗する
- **THEN** エラーがログに記録され、ジョブのステータス遷移には影響しない

### Requirement: Discord 通知アダプター

システムは Discord Webhook 経由で通知を送信する `DiscordNotificationSender` アダプターを提供しなければならない（SHALL）。Webhook URL は環境変数 `DISCORD_WEBHOOK_URL` から取得する。

#### Scenario: ジョブ完了時の Discord 通知
- **WHEN** ジョブが COMPLETED 状態に遷移し、notification_channel が DISCORD である
- **THEN** ジョブ ID とステータスを含むメッセージが Discord Webhook に POST される

#### Scenario: ジョブ失敗時の Discord 通知
- **WHEN** ジョブが FAILED 状態に遷移し、notification_channel が DISCORD である
- **THEN** ジョブ ID、ステータス、エラー情報を含むメッセージが Discord Webhook に POST される

#### Scenario: Webhook 送信失敗時のフォールバック
- **WHEN** Discord Webhook への HTTP リクエストが失敗する
- **THEN** エラーがログに記録され、ジョブのステータス遷移には影響しない

### Requirement: NullNotificationSender

システムは通知チャネルが NONE の場合に何も送信しない `NullNotificationSender` を提供しなければならない（SHALL）。

#### Scenario: 通知なしの場合
- **WHEN** ジョブの notification_channel が NONE であり、send が呼ばれる
- **THEN** 何も実行されず、正常に処理が完了する

### Requirement: NotificationSenderFactory によるアダプター解決

システムは `NotificationChannel` の値に基づいて適切な `NotificationSender` 実装を返すファクトリを提供しなければならない（SHALL）。

#### Scenario: EMAIL チャネルのアダプター解決
- **WHEN** NotificationSenderFactory に NotificationChannel.EMAIL が渡される
- **THEN** EmailNotificationSender が返される

#### Scenario: DISCORD チャネルのアダプター解決
- **WHEN** NotificationSenderFactory に NotificationChannel.DISCORD が渡される
- **THEN** DiscordNotificationSender が返される

#### Scenario: NONE チャネルのアダプター解決
- **WHEN** NotificationSenderFactory に NotificationChannel.NONE が渡される
- **THEN** NullNotificationSender が返される

### Requirement: ワーカーによる通知送信

ワーカーはジョブの完了または失敗後に、ジョブの notification_channel に基づいて通知を送信しなければならない（SHALL）。通知送信はジョブのステータス遷移の後に実行され、通知の失敗がジョブの処理に影響してはならない。

#### Scenario: ジョブ完了後の通知
- **WHEN** ワーカーがジョブを COMPLETED に遷移させる
- **THEN** NotificationSenderFactory でアダプターを解決し、send を呼び出す

#### Scenario: ジョブ失敗後の通知
- **WHEN** ワーカーがジョブを FAILED に遷移させる
- **THEN** NotificationSenderFactory でアダプターを解決し、send を呼び出す

#### Scenario: 通知失敗がジョブ処理に影響しない
- **WHEN** 通知送信中に例外が発生する
- **THEN** 例外はキャッチされてログに記録され、ジョブのステータスは変更されない

### Requirement: ローカル開発での MailPit 連携

Docker Compose 環境では MailPit コンテナを SMTP サーバーとして使用し、Email 通知をローカルで検証できなければならない（SHALL）。

#### Scenario: MailPit で Email を受信確認
- **WHEN** Email 通知が送信される（ローカル開発環境）
- **THEN** MailPit の Web UI（http://localhost:8025）で送信されたメールの内容を確認できる

### Requirement: 通知設定の環境変数

システムは以下の環境変数で通知先を設定できなければならない（SHALL）。

| 環境変数 | 説明 | デフォルト値 |
|---|---|---|
| SMTP_HOST | SMTP サーバーホスト | mailpit |
| SMTP_PORT | SMTP サーバーポート | 1025 |
| NOTIFICATION_EMAIL_FROM | 送信元メールアドレス | noreply@jobworker.local |
| NOTIFICATION_EMAIL_TO | 送信先メールアドレス | user@jobworker.local |
| DISCORD_WEBHOOK_URL | Discord Webhook URL | （空文字列） |

#### Scenario: 環境変数によるSMTP設定
- **WHEN** SMTP_HOST と SMTP_PORT が設定されている
- **THEN** EmailNotificationSender はその値を使用して SMTP サーバーに接続する

#### Scenario: 環境変数による Discord 設定
- **WHEN** DISCORD_WEBHOOK_URL が設定されている
- **THEN** DiscordNotificationSender はその URL に Webhook メッセージを POST する
