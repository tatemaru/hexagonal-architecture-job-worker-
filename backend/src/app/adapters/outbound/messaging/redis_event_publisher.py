"""Redis Pub/Sub によるイベントパブリッシャーの実装。

EventPublisher ポートの具象クラス。
ドメインイベントを JSON シリアライズし、Redis の job_events チャンネルに Publish する。
ワーカーや SSE エンドポイントがこのチャンネルを Subscribe してイベントを受信する。
"""

import json

import redis.asyncio as aioredis

from app.domain.events.job_events import DomainEvent
from app.ports.event_publisher import EventPublisher

CHANNEL = "job_events"
"""Redis Pub/Sub のチャンネル名。全ドメインイベントがこのチャンネルで配信される。"""


class RedisEventPublisher(EventPublisher):
    """Redis Pub/Sub を使った EventPublisher の実装。

    ヘキサゴナルアーキテクチャのセカンダリアダプター（出力側）として、
    ドメインイベントのプロセス間配信を担当する。
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def publish(self, event: DomainEvent) -> None:
        """ドメインイベントを JSON 形式で Redis チャンネルに Publish する。

        メッセージ形式:
            {"event_type": "JobCreated", "job_id": "<uuid>", "timestamp": "<ISO8601>"}
        """
        message = json.dumps(
            {
                "event_type": event.event_type,
                "job_id": str(event.job_id),
                "timestamp": event.timestamp.isoformat(),
            }
        )
        await self._redis.publish(CHANNEL, message)
