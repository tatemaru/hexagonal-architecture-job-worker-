# Hexagonal Architecture Job Worker

FastAPI + PostgreSQL + Redis を使ったジョブ実行アプリ（学習用）。
DDD とヘキサゴナルアーキテクチャを前提に、API / ワーカー / 通知 / SSE を分離して実装しています。

## 特徴

- ジョブ作成・一覧・詳細・キャンセル API
- Redis Pub/Sub によるイベント配信
- ワーカーによる非同期ジョブ実行
- SSE によるリアルタイム更新
- Email / Discord 通知（ローカルは Mailpit）

## ドキュメント

- バックエンド実装ガイド: `docs/backend/README.md`

## 構成

```
backend/   # FastAPI + ドメイン/ユースケース/アダプター
frontend/  # Vite + React
openspec/  # 仕様管理（OpenSpec）
docs/      # ドキュメント
```

## クイックスタート（Docker Compose）

```bash
docker compose up --build
```

起動後:
- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Mailpit UI: `http://localhost:8025`

※ URL はコードブロック内に記載しています。

## ローカル開発（個別起動）

### Backend

```bash
cd backend
uv sync --no-dev
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Worker

```bash
cd backend
uv run python -m app.worker
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

## 環境変数

`docker-compose.yml` で使用する主な環境変数:

- `DATABASE_URL`
- `REDIS_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `SMTP_HOST`
- `SMTP_PORT`
- `NOTIFICATION_EMAIL_FROM`
- `NOTIFICATION_EMAIL_TO`
- `DISCORD_WEBHOOK_URL`
- `DISCORD_WEBHOOK_THREAD_NAME`

## 主要エントリポイント

- API: `backend/src/app/main.py`
- Worker: `backend/src/app/worker.py`
- Router: `backend/src/app/adapters/inbound/api/job_router.py`

## ライセンス

TBD
