"""ジョブ作成ユースケース。

新しいジョブを作成し、永続化した後、JobCreated イベントを配信する。
"""

from app.domain.models.job import Job, JobType
from app.domain.models.notification import NotificationChannel
from app.ports.event_publisher import EventPublisher
from app.ports.repository import JobRepository


class CreateJobUseCase:
    """ジョブを新規作成するユースケース。

    ドメインの Job.create() を呼び出し、リポジトリに保存し、
    発生したドメインイベントをパブリッシャー経由で配信する。
    """

    def __init__(self, repository: JobRepository, publisher: EventPublisher) -> None:
        self._repository = repository
        self._publisher = publisher

    async def execute(
        self,
        duration_seconds: int,
        notification_channel: NotificationChannel = NotificationChannel.NONE,
    ) -> Job:
        """指定された実行秒数でジョブを作成する。

        Args:
            duration_seconds: ダミージョブの実行秒数。
            notification_channel: 通知チャネル（デフォルト: NONE）。

        Returns:
            作成された Job（PENDING 状態）。
        """
        job = Job.create(
            JobType(duration_seconds=duration_seconds),
            notification_channel=notification_channel,
        )
        await self._repository.save(job)
        for event in job.collect_events():
            await self._publisher.publish(event)
        return job
