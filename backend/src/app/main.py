"""FastAPI アプリケーションのエントリーポイント。

起動時に以下を行う:
    - PostgreSQL に jobs テーブルを作成する（存在しない場合）
    - Redis クライアントを初期化し、app.state に保持する

終了時に以下を行う:
    - Redis 接続をクローズする
    - DB エンジンを破棄する

ルーターの登録順序に注意:
    SSE ルーター（/api/jobs/stream）を先に登録し、
    REST ルーター（/api/jobs/{job_id}）より優先させる。
    逆にすると /stream が {job_id} パラメータにマッチしてしまう。
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from app.adapters.outbound.persistence.database import engine
from app.adapters.outbound.persistence.models import Base

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理。起動・終了時の初期化・後片付けを行う。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.redis = aioredis.from_url(REDIS_URL)
    yield
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(title="Job Worker", lifespan=lifespan)

from app.adapters.inbound.api.job_router import router as job_router  # noqa: E402
from app.adapters.inbound.sse.job_sse import router as sse_router  # noqa: E402

# SSE ルーターを先に登録する（/stream が /{job_id} より優先されるように）
app.include_router(sse_router)
app.include_router(job_router)
