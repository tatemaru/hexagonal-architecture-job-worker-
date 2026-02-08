## 1. プロジェクト基盤・Docker 環境

- [x] 1.1 backend/ ディレクトリを作成し、uv で Python プロジェクトを初期化する（pyproject.toml）
- [x] 1.2 backend/Dockerfile を作成する（uv でのパッケージインストール、uvicorn 起動）
- [x] 1.3 frontend/ ディレクトリを作成し、bun + Vite + React + TypeScript でプロジェクトを初期化する
- [x] 1.4 frontend/Dockerfile を作成する（bun でのパッケージインストール、Vite 開発サーバー起動）
- [x] 1.5 docker-compose.yml を作成する（api, worker, frontend, postgres, redis の5サービス定義、ボリュームマウント、depends_on 設定）

## 2. ドメイン層

- [x] 2.1 値オブジェクトを実装する（JobId, JobStatus, JobType, JobResult）
- [x] 2.2 JobStatus にステートマシンの遷移ルールを実装する（許可される遷移の定義、禁止遷移時の例外）
- [x] 2.3 ドメインイベントを定義する（JobCreated, JobStarted, JobCompleted, JobFailed, JobCancelled）
- [x] 2.4 ドメイン例外を定義する（InvalidStatusTransitionError, JobNotFoundError）
- [x] 2.5 Job 集約ルートを実装する（start, complete, fail, cancel メソッドと状態遷移 + イベント発行）

## 3. ポート層

- [x] 3.1 JobRepository ポート（抽象基底クラス）を定義する（save, find_by_id, find_all）
- [x] 3.2 EventPublisher ポート（抽象基底クラス）を定義する（publish）

## 4. ユースケース層

- [x] 4.1 CreateJobUseCase を実装する（Job 作成 → 永続化 → JobCreated イベント配信）
- [x] 4.2 GetJobUseCase を実装する（JobId による詳細取得）
- [x] 4.3 ListJobsUseCase を実装する（全ジョブ一覧取得、作成日時降順）
- [x] 4.4 CancelJobUseCase を実装する（Job 取得 → cancel() → 永続化 → JobCancelled イベント配信）

## 5. アダプター層 — セカンダリ（永続化・メッセージング）

- [x] 5.1 SQLAlchemy モデル（jobs テーブル）を定義する
- [x] 5.2 DB 接続設定とセッション管理を実装する（async SQLAlchemy + asyncpg）
- [x] 5.3 PostgresJobRepository を実装する（JobRepository ポートの具象クラス）
- [x] 5.4 RedisEventPublisher を実装する（EventPublisher ポートの具象クラス、job_events チャンネルに JSON を Publish）

## 6. アダプター層 — プライマリ（API・SSE）

- [x] 6.1 FastAPI アプリケーションのエントリーポイント（main.py）を作成する（起動時に DB テーブル作成を含む）
- [x] 6.2 POST /api/jobs エンドポイントを実装する（CreateJobUseCase を呼び出し、201 レスポンス）
- [x] 6.3 GET /api/jobs エンドポイントを実装する（ListJobsUseCase を呼び出し）
- [x] 6.4 GET /api/jobs/{job_id} エンドポイントを実装する（GetJobUseCase を呼び出し）
- [x] 6.5 POST /api/jobs/{job_id}/cancel エンドポイントを実装する（CancelJobUseCase を呼び出し）
- [x] 6.6 GET /api/jobs/stream SSE エンドポイントを実装する（Redis Subscribe → SSE ストリーム変換、切断時のクリーンアップ）

## 7. ワーカープロセス

- [x] 7.1 ワーカーのエントリーポイント（app/worker.py）を作成する（Redis Subscribe 開始）
- [x] 7.2 JobCreated イベント受信 → Job 取得 → start() → JobStarted Publish のフローを実装する
- [x] 7.3 ダミージョブ実行ループを実装する（1秒間隔の sleep + キャンセルフラグポーリング）
- [x] 7.4 ジョブ完了処理を実装する（complete() → JobCompleted Publish）
- [x] 7.5 ジョブ失敗処理を実装する（fail() → JobFailed Publish、エラー情報を JobResult に記録）

## 8. フロントエンド

- [x] 8.1 API クライアント（jobApi.ts）を作成する（POST /api/jobs, GET /api/jobs, GET /api/jobs/{id}, POST /api/jobs/{id}/cancel）
- [x] 8.2 SSE 接続カスタムフック（useJobSSE.ts）を作成する（EventSource で /api/jobs/stream に接続、イベント受信時にコールバック実行）
- [x] 8.3 JobStatusBadge コンポーネントを作成する（ステータスごとの色分けバッジ: PENDING=灰, RUNNING=青, COMPLETED=緑, FAILED=赤, CANCELLED=黄）
- [x] 8.4 JobCreateForm コンポーネントを作成する（実行秒数入力フォーム + バリデーション）
- [x] 8.5 JobList コンポーネントを作成する（一覧テーブル + キャンセルボタン表示制御）
- [x] 8.6 App.tsx で全コンポーネントを組み合わせる（初期データ取得 + SSE によるリアルタイム更新）
- [x] 8.7 Vite の proxy 設定を追加する（開発時に /api を API サーバーへプロキシ）

## 9. 結合・動作確認

- [x] 9.1 docker compose up で全サービスが起動することを確認する
- [x] 9.2 ブラウザからジョブ作成 → ワーカー実行 → リアルタイムステータス更新の一連のフローを確認する
- [x] 9.3 ジョブのキャンセル（PENDING・RUNNING 両方）が動作することを確認する
