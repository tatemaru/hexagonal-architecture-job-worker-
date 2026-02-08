"""ジョブ一覧取得ユースケース。

全ジョブを作成日時の降順で取得する。
"""

from app.domain.models.job import Job
from app.ports.repository import JobRepository


class ListJobsUseCase:
    """ジョブの一覧を取得するユースケース。"""

    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[Job]:
        """全ジョブを作成日時の降順で返す。"""
        return await self._repository.find_all()
