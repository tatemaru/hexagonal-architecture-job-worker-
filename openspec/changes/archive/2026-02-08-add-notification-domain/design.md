## Context

現在のシステムはジョブの状態変化を SSE 経由でブラウザにリアルタイム配信しているが、ブラウザを閉じるとイベントを受け取れない。ジョブ完了・失敗の通知を Email または Discord で外部に送信する仕組みを追加する。

既存アーキテクチャはヘキサゴナルパターンに従い、ドメイン層（Job aggregate、DomainEvent）、ポート層（JobRepository、EventPublisher）、アダプター層（PostgreSQL、Redis Pub/Sub）が明確に分離されている。通知機能もこのパターンに沿って追加する。

## Goals / Non-Goals

**Goals:**
- ジョブ完了（JobCompleted）・失敗（JobFailed）時に Email または Discord で通知を送信する
- ジョブ作成時に通知チャネル（email / discord / none）を選択可能にする
- ヘキサゴナルアーキテクチャのパターンを維持し、通知送信を抽象ポート経由で行う
- 既存のワーカープロセスに通知ロジックを組み込み、新規プロセスを増やさない

**Non-Goals:**
- 通知テンプレートのカスタマイズ機能
- 通知送信のリトライ・キュー機能（失敗時はログ出力のみ）
- 通知履歴の永続化・管理画面
- 複数チャネルへの同時通知（1ジョブにつき1チャネル）
- Email 宛先やDiscord Webhook URL のジョブ単位での指定（環境変数でグローバル設定）

## Decisions

### 1. 通知チャネルを Job aggregate の値オブジェクトとして定義する

**決定:** `NotificationChannel` を `Enum`（`NONE`, `EMAIL`, `DISCORD`）として Job ドメインモデルに追加する。

**理由:** 通知先の選択はジョブ作成時のビジネス要件であり、ドメインの関心事。Job aggregate が自身の通知設定を保持するのが自然。独立した Notification aggregate を作るほどの複雑性はない。

**代替案:**
- 独立した Notification aggregate → ジョブとの1:1対応で冗長。将来通知が複雑化した場合に検討する。
- ユースケース層で通知先を決定 → ドメイン知識がユースケースに漏れる。

### 2. NotificationSender ポートを新設する

**決定:** `NotificationSender` を抽象基底クラスとして `ports/` に定義し、`send(job: Job) -> None` メソッドを持たせる。Email と Discord のアダプターがこれを実装する。

**理由:** ヘキサゴナルアーキテクチャのパターンに従い、通知送信の技術的詳細をドメイン・ユースケース層から隔離する。

**代替案:**
- EventPublisher を拡張する → 責務が異なる（イベント配信 vs 外部通知）。単一責任原則に反する。

### 3. 既存ワーカーに通知ロジックを組み込む

**決定:** `worker.py` の `execute_job` 完了後・失敗後に NotificationSender を呼び出す。新しいプロセスは作らない。

**理由:** ワーカーは既にジョブの完了・失敗を処理しており、通知はその延長。新プロセスを追加するとインフラ複雑性が増す。

**代替案:**
- 独立した通知ワーカープロセス → Redis Pub/Sub で JobCompleted/JobFailed を購読する方式。スケーラビリティは上がるが、現時点ではオーバーエンジニアリング。

### 4. Email は SMTP、Discord は Webhook で実装する

**決定:**
- Email: Python 標準ライブラリの `smtplib`（`aiosmtplib` で非同期化）を使用。SMTP サーバー設定は環境変数で管理。
- Discord: `httpx`（既に非同期 HTTP クライアントとして一般的）で Webhook URL に POST。

**理由:** 最小限の依存で実現できる。Email は SMTP が標準、Discord は Webhook API が公式推奨。

**代替案:**
- SendGrid / SES 等の API → 外部サービス依存が増える。学習用プロジェクトには過剰。
- Discord Bot API → Webhook より設定が複雑。通知送信だけなら Webhook で十分。

### 4a. ローカル開発での Email 検証に MailPit を使用する

**決定:** Docker Compose に MailPit コンテナを追加し、ローカル開発環境での SMTP 送信先として使用する。MailPit は SMTP サーバー（ポート 1025）と Web UI（ポート 8025）を提供し、送信されたメールをブラウザで確認できる。

**理由:** 実際の SMTP サーバーやメールアカウントを用意せずに、ローカルで Email 通知の動作確認ができる。開発中に誤って外部にメールを送信するリスクもない。

**環境変数のデフォルト値:**
- `SMTP_HOST=mailpit`（Docker Compose サービス名）
- `SMTP_PORT=1025`（MailPit の SMTP ポート）
- MailPit Web UI: `http://localhost:8025`

### 5. 通知チャネルの解決にファクトリパターンを使う

**決定:** `NotificationSenderFactory` を用意し、`NotificationChannel` の値に基づいて適切な `NotificationSender` 実装を返す。`NONE` の場合は何もしない `NullNotificationSender` を返す。

**理由:** ワーカー側の条件分岐を排除し、Open-Closed Principle に従う。新しいチャネル追加時にファクトリに登録するだけで済む。

### 6. 通知先設定は環境変数でグローバルに管理する

**決定:** Email 宛先（`NOTIFICATION_EMAIL_TO`, `SMTP_HOST`, `SMTP_PORT` 等）と Discord Webhook URL（`DISCORD_WEBHOOK_URL`）は環境変数で設定する。ジョブ単位での指定はしない。

**理由:** 学習用プロジェクトとしてシンプルさを優先。ユーザー管理機能がないため、グローバル設定で十分。

## Risks / Trade-offs

- **SMTP 接続失敗でジョブ完了が遅延する** → 通知送信は try-except で囲み、失敗してもジョブのステータス遷移には影響させない。ログにエラーを記録するのみ。
- **Discord Webhook URL の漏洩リスク** → 環境変数で管理し、コードにハードコードしない。docker-compose.yml では `.env` ファイルから読み込む。
- **通知の重複送信** → ワーカーが1つのため現時点では問題ないが、ワーカーを複数台にスケールする場合は排他制御が必要になる。現時点では対象外。
- **非同期 SMTP ライブラリの追加依存** → `aiosmtplib` を追加する必要がある。軽量で広く使われているため影響は小さい。
