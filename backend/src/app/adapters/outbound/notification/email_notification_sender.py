"""Email 通知アダプター。

SMTP 経由でジョブの完了・失敗通知を送信する。
ローカル開発では MailPit を SMTP サーバーとして使用する。
"""

import logging
import os
from email.message import EmailMessage

import aiosmtplib

from app.domain.models.job import Job
from app.ports.notification_sender import NotificationSender

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST", "mailpit")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
EMAIL_FROM = os.environ.get("NOTIFICATION_EMAIL_FROM", "noreply@jobworker.local")
EMAIL_TO = os.environ.get("NOTIFICATION_EMAIL_TO", "user@jobworker.local")


class EmailNotificationSender(NotificationSender):
    """SMTP を使った通知送信の実装。"""

    async def send(self, job: Job) -> str | None:
        """ジョブの状態に基づいて Email 通知を送信する。"""
        msg = EmailMessage()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = f"[JobWorker] Job {job.id} - {job.status.value}"

        body = f"Job ID: {job.id}\nStatus: {job.status.value}\n"
        if job.result:
            body += f"Message: {job.result.message}\n"
            if job.result.error:
                body += f"Error: {job.result.error}\n"
        msg.set_content(body)

        await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT)
        logger.info("Email notification sent for job %s", job.id)
        return None
