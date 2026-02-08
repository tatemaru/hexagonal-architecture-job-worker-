"""ジョブワーカープロセス。

API サーバーとは独立したプロセスとして動作し、
Redis Pub/Sub の job_events チャンネルを Subscribe して
JobCreated イベントを受信・ジョブを実行する。

起動コマンド: python -m app.worker

処理フロー:
    1. Redis Pub/Sub を Subscribe してイベントを待機する
    2. JobCreated イベントを受信したら、Job を RUNNING に遷移させる
    3. ダミージョブ（指定秒数の sleep）を実行する
    4. 実行中は1秒間隔で DB をポーリングし、キャンセルを検知する
    5. 完了したら COMPLETED に、失敗したら FAILED に遷移させる
"""

import asyncio
import json
import logging
import os
import traceback

import redis.asyncio as aioredis

from app.adapters.outbound.messaging.redis_event_publisher import (
    CHANNEL,
    RedisEventPublisher,
)
from app.adapters.outbound.notification.notification_sender_factory import (
    NotificationSenderFactory,
)
from app.adapters.outbound.persistence.database import async_session
from app.adapters.outbound.persistence.postgres_job_repository import (
    PostgresJobRepository,
)
from app.domain.models.job import JobId, JobResult, JobStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker] %(message)s")
logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


async def execute_job(
    job_id: JobId,
    duration: int,
    repo: PostgresJobRepository,
    publisher: RedisEventPublisher,
) -> None:
    """ダミージョブを実行する（指定秒数の sleep）。

    1秒ごとに DB をポーリングしてキャンセルフラグを確認する。
    キャンセルされていた場合は即座に中断する。
    完了後は Job を COMPLETED に遷移させ、イベントを配信する。
    """
    elapsed = 0
    while elapsed < duration:
        await asyncio.sleep(1)
        elapsed += 1
        async with async_session() as session:
            poll_repo = PostgresJobRepository(session)
            job = await poll_repo.find_by_id(job_id)
            if job is None or job.status == JobStatus.CANCELLED:
                logger.info("Job %s was cancelled, aborting", job_id)
                return

    async with async_session() as session:
        complete_repo = PostgresJobRepository(session)
        job = await complete_repo.find_by_id(job_id)
        if job is None or job.status == JobStatus.CANCELLED:
            return
        job.complete(JobResult(message=f"Completed after {duration}s"))
        await complete_repo.save(job)
        for event in job.collect_events():
            await publisher.publish(event)
        logger.info("Job %s completed", job_id)

        try:
            sender = NotificationSenderFactory.create(job.notification_channel)
            await sender.send(job)
        except Exception:
            logger.error(
                "Failed to send notification for job %s: %s",
                job_id,
                traceback.format_exc(),
            )


async def handle_event(data: dict, redis_client: aioredis.Redis) -> None:
    """Redis Pub/Sub から受信したイベントを処理する。

    JobCreated イベントのみを対象とし、以下の処理を行う:
        1. Job を DB から取得する
        2. start() で RUNNING に遷移させ、JobStarted を配信する
        3. ダミージョブを実行する
        4. 失敗した場合は fail() で FAILED に遷移させ、JobFailed を配信する
    """
    event_type = data.get("event_type")
    if event_type != "JobCreated":
        return

    job_id = JobId(data["job_id"])
    logger.info("Received JobCreated for %s", job_id)

    async with async_session() as session:
        repo = PostgresJobRepository(session)
        publisher = RedisEventPublisher(redis_client)

        job = await repo.find_by_id(job_id)
        if job is None:
            logger.error("Job %s not found", job_id)
            return

        try:
            job.start()
            await repo.save(job)
            for event in job.collect_events():
                await publisher.publish(event)
            logger.info(
                "Job %s started (duration=%ds)", job_id, job.job_type.duration_seconds
            )
        except Exception:
            logger.error("Failed to start job %s: %s", job_id, traceback.format_exc())
            return

        try:
            sender = NotificationSenderFactory.create(job.notification_channel)
            thread_id = await sender.send(job)
            if thread_id:
                job.discord_thread_id = thread_id
                await repo.save(job)
                logger.info("Stored discord_thread_id=%s for job %s", thread_id, job_id)
        except Exception:
            logger.error(
                "Failed to send start notification for job %s: %s",
                job_id,
                traceback.format_exc(),
            )

    try:
        publisher = RedisEventPublisher(redis_client)
        await execute_job(job_id, job.job_type.duration_seconds, repo, publisher)
    except Exception:
        logger.error("Job %s failed: %s", job_id, traceback.format_exc())
        async with async_session() as session:
            fail_repo = PostgresJobRepository(session)
            publisher = RedisEventPublisher(redis_client)
            job = await fail_repo.find_by_id(job_id)
            if job and job.status == JobStatus.RUNNING:
                job.fail(JobResult(message="Job failed", error=traceback.format_exc()))
                await fail_repo.save(job)
                for event in job.collect_events():
                    await publisher.publish(event)

                try:
                    sender = NotificationSenderFactory.create(job.notification_channel)
                    await sender.send(job)
                except Exception:
                    logger.error(
                        "Failed to send notification for job %s: %s",
                        job_id,
                        traceback.format_exc(),
                    )


async def main() -> None:
    """ワーカーのメインループ。

    Redis Pub/Sub を Subscribe し、イベントを受信するたびに
    handle_event を非同期タスクとして起動する。
    """
    logger.info("Worker starting, connecting to Redis at %s", REDIS_URL)
    redis_client = aioredis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(CHANNEL)
    logger.info("Subscribed to channel '%s', waiting for events...", CHANNEL)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                asyncio.create_task(handle_event(data, redis_client))
            else:
                await asyncio.sleep(0.1)
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await pubsub.aclose()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
