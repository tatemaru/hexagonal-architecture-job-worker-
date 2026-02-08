"""通知アダプターのファクトリ。

NotificationChannel の値に基づいて適切な NotificationSender 実装を返す。
"""

from app.adapters.outbound.notification.discord_notification_sender import (
    DiscordNotificationSender,
)
from app.adapters.outbound.notification.email_notification_sender import (
    EmailNotificationSender,
)
from app.adapters.outbound.notification.null_notification_sender import (
    NullNotificationSender,
)
from app.domain.models.notification import NotificationChannel
from app.ports.notification_sender import NotificationSender


class NotificationSenderFactory:
    """NotificationChannel に基づいて NotificationSender を生成するファクトリ。"""

    @staticmethod
    def create(channel: NotificationChannel) -> NotificationSender:
        """指定されたチャネルに対応する NotificationSender を返す。"""
        if channel == NotificationChannel.EMAIL:
            return EmailNotificationSender()
        if channel == NotificationChannel.DISCORD:
            return DiscordNotificationSender()
        return NullNotificationSender()
