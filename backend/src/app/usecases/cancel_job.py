"""ジョブキャンセルユースケース。

指定されたジョブをキャンセルし、永続化した後、JobCancelled イベントを配信する。
PENDING または RUNNING 状態のジョブのみキャンセル可能。
"""

from app.domain.exceptions import JobNotFoundError
from app.domain.models.job import Job, JobId
from app.ports.event_publisher import EventPublisher
from app.ports.repository import JobRepository


class CancelJobUseCase:
    """ジョブをキャンセルするユースケース。

    Job 集約の cancel() を呼び出し、リポジトリに保存し、
    発生したドメインイベントをパブリッシャー経由で配信する。
    """

    def __init__(self, repository: JobRepository, publisher: EventPublisher) -> None:
        self._repository = repository
        self._publisher = publisher

    async def execute(self, job_id: JobId) -> Job:
        """指定された ID のジョブをキャンセルする。

        Args:
            job_id: キャンセル対象のジョブ ID。

        Returns:
            キャンセル後の Job（CANCELLED 状態）。

        Raises:
            JobNotFoundError: ジョブが見つからない場合。
            InvalidStatusTransitionError: COMPLETED/FAILED 状態のジョブをキャンセルしようとした場合。
        """
        job = await self._repository.find_by_id(job_id)
        if job is None:
            raise JobNotFoundError(str(job_id))
        job.cancel()
        await self._repository.save(job)
        for event in job.collect_events():
            await self._publisher.publish(event)
        return job
