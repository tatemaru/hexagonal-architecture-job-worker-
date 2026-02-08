## Why

ジョブの状態変化（完了・失敗など）をユーザーに外部通知する仕組みが存在しない。現在はSSEによるリアルタイムUI更新のみで、ブラウザを閉じると状態変化を見逃す。Email と Discord の通知チャネルを選択可能にし、ジョブ完了や失敗を確実にユーザーへ届ける。

## What Changes

- 通知ドメインの新規追加（Notification aggregate、NotificationChannel value object）
- 通知ポート（NotificationSender）の定義
- Email アダプターの実装（SMTP経由）
- Discord アダプターの実装（Webhook経由）
- ジョブ作成時に通知チャネル（email / discord / none）を選択可能にする
- ジョブ完了・失敗時にドメインイベントを購読して通知を送信するワーカーまたはイベントハンドラの追加
- フロントエンドのジョブ作成フォームに通知チャネル選択UIを追加

## Capabilities

### New Capabilities
- `notification`: 通知ドメインモデル、通知ポート（NotificationSender）、Email/Discord アダプター、ドメインイベント購読による通知送信を扱う

### Modified Capabilities
- `job-management`: Job aggregate に通知チャネル設定（notification_channel）を追加。ジョブ作成時に通知先を指定できるようにする
- `frontend-ui`: ジョブ作成フォームに通知チャネル選択（Email / Discord / なし）のUIを追加

## Impact

- **ドメイン層**: 新規 notification ドメインモデル追加、Job モデルに notification_channel フィールド追加
- **ポート層**: NotificationSender ポート新規追加
- **アダプター層**: EmailNotificationSender、DiscordNotificationSender アダプター新規追加
- **ユースケース層**: 通知送信ユースケース追加、またはイベントハンドラとして実装
- **永続化**: jobs テーブルに notification_channel カラム追加
- **外部依存**: SMTP サーバー接続設定、Discord Webhook URL 設定
- **Docker**: 環境変数に SMTP 設定、Discord Webhook URL を追加
- **フロントエンド**: JobCreateForm に通知チャネル選択のセレクトボックスを追加、API リクエストに notification_channel を含める
