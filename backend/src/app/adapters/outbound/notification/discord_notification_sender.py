"""Discord 通知アダプター。

Discord Webhook 経由でジョブの開始・完了・失敗通知を送信する。
フォーラムチャネルの場合、開始通知で新しいスレッドを作成し、
完了・失敗通知では同じスレッドに返信する。
"""

import logging
import os

import httpx

from app.domain.models.job import Job, JobStatus
from app.ports.notification_sender import NotificationSender

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


class DiscordNotificationSender(NotificationSender):
    """Discord Webhook を使った通知送信の実装。"""

    async def send(self, job: Job) -> str | None:
        """ジョブの状態に基づいて Discord 通知を送信する。

        Returns:
            フォーラムスレッド作成時はスレッドID、それ以外は None。
        """
        content = f"**[JobWorker]** Job `{job.id}` - **{job.status.value}**"
        if job.result:
            content += f"\nMessage: {job.result.message}"
            if job.result.error:
                content += f"\nError: {job.result.error}"

        payload: dict = {"content": content}
        url = DISCORD_WEBHOOK_URL
        thread_id: str | None = None

        thread_name = os.environ.get("DISCORD_WEBHOOK_THREAD_NAME", "")

        if job.discord_thread_id:
            # 既存スレッドに返信
            url = f"{DISCORD_WEBHOOK_URL}?thread_id={job.discord_thread_id}"
        elif thread_name:
            # 新しいスレッドを作成（開始通知時）
            payload["thread_name"] = thread_name
            url = f"{DISCORD_WEBHOOK_URL}?wait=true"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if not response.is_success:
                logger.error(
                    "Discord API error for job %s: %s %s",
                    job.id,
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()

            # ?wait=true の場合、レスポンスにスレッドIDが含まれる
            if thread_name and not job.discord_thread_id:
                data = response.json()
                thread_id = data.get("channel_id")
                logger.info(
                    "Discord thread created for job %s: thread_id=%s",
                    job.id,
                    thread_id,
                )

        logger.info("Discord notification sent for job %s", job.id)
        return thread_id
