# FastAPI / Python / Redis 入門（最低限）

この章は「このコードを読むのに必要な最低限の知識」を短く押さえるためのものです。詳細を学ぶためではなく、実装を追うための“足場”として読んでください。

## FastAPI の超基本

FastAPI は Python の Web フレームワークです。主に以下を理解しておけば十分です。

- **APIRouter** でルーティング（URL と関数を結び付ける）
- **Depends** で依存関係（DB セッションなど）を注入
- **Pydantic** でリクエスト/レスポンスの型定義

例（実装上の位置）:
- ルーター: `backend/src/app/adapters/inbound/api/job_router.py`
- リクエスト/レスポンスモデル: 同ファイル内の `CreateJobRequest`, `JobResponse`

## Python（非同期）の最低限

このアプリは `async/await` を多用します。大事なのは「I/O 待ち中に他の処理を進められる」ことです。

- `async def` は非同期関数
- `await` は I/O 待ち（DB、Redis、HTTP など）
- CPU を大量に使う処理はこのアプリにはほぼない

## Redis の使い方（このアプリの範囲）

このアプリが使う Redis は **Pub/Sub** と **共有接続** の 2 つです。

- **Pub/Sub**: イベントを配信し、ワーカーや SSE が受信
- **共有接続**: FastAPI 起動時に接続を作成し `app.state.redis` に保持

実装箇所:
- Redis 接続管理: `backend/src/app/main.py`
- イベント配信: `backend/src/app/adapters/outbound/messaging/redis_event_publisher.py`
- SSE 受信: `backend/src/app/adapters/inbound/sse/job_sse.py`
- ワーカー受信: `backend/src/app/worker.py`

ここまで理解できれば、後続の章で具体的な流れを追えます。
