"""Null 通知アダプター。

通知チャネルが NONE の場合に使用される。何も送信しない。
"""

from app.domain.models.job import Job
from app.ports.notification_sender import NotificationSender


class NullNotificationSender(NotificationSender):
    """何も送信しない通知アダプター。"""

    async def send(self, job: Job) -> str | None:
        """何もしない。"""
        return None
