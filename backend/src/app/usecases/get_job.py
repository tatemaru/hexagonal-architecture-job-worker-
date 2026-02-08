"""ジョブ詳細取得ユースケース。

指定された JobId のジョブを取得する。存在しない場合は JobNotFoundError をスローする。
"""

from app.domain.exceptions import JobNotFoundError
from app.domain.models.job import Job, JobId
from app.ports.repository import JobRepository


class GetJobUseCase:
    """ジョブの詳細情報を取得するユースケース。"""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(self, job_id: JobId) -> Job:
        """指定された ID のジョブを取得する。

        Args:
            job_id: 取得対象のジョブ ID。

        Returns:
            該当する Job。

        Raises:
            JobNotFoundError: ジョブが見つからない場合。
        """
        job = await self._repository.find_by_id(job_id)
        if job is None:
            raise JobNotFoundError(str(job_id))
        return job
