"""SSE（Server-Sent Events）エンドポイント（プライマリアダプター）。

ヘキサゴナルアーキテクチャのプライマリアダプター（入力側）として、
Redis Pub/Sub のドメインイベントを購読し、SSE ストリームに変換して
ブラウザにリアルタイム配信する。

接続の仕組み:
    1. クライアントが GET /api/jobs/stream に接続する
    2. サーバーが Redis の job_events チャンネルを Subscribe する
    3. イベントを受信するたびに SSE 形式でクライアントに送信する
    4. クライアントが切断したらリソースをクリーンアップする
"""

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from app.adapters.outbound.messaging.redis_event_publisher import CHANNEL

router = APIRouter(prefix="/api/jobs", tags=["sse"])


@router.get("/stream")
async def job_stream(request: Request) -> StreamingResponse:
    """GET /api/jobs/stream - ドメインイベントを SSE で配信する。

    Content-Type: text/event-stream のレスポンスを返し、
    接続を維持したままイベントデータを逐次送信する。
    """
    redis: aioredis.Redis = request.app.state.redis
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL)

    async def event_generator():
        """Redis Pub/Sub からイベントを受信し、SSE 形式に変換して yield する。

        SSE の出力形式:
            event: JobStarted
            data: {"event_type": "JobStarted", "job_id": "<uuid>", "timestamp": "<ISO8601>"}
        """
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    event_type = data["event_type"]
                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                else:
                    await asyncio.sleep(0.1)
        finally:
            await pubsub.unsubscribe(CHANNEL)
            await pubsub.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
