"""PostgreSQL によるジョブリポジトリの実装。

JobRepository ポートの具象クラス。
SQLAlchemy の async セッションを使用して PostgreSQL にアクセスし、
ORM モデル（JobRow）とドメインモデル（Job）の変換を行う。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import JobRow
from app.domain.models.job import (
    Job,
    JobId,
    JobResult,
    JobStatus,
    JobType,
)
from app.domain.models.notification import NotificationChannel
from app.ports.repository import JobRepository


class PostgresJobRepository(JobRepository):
    """PostgreSQL を使った JobRepository の実装。

    ヘキサゴナルアーキテクチャのセカンダリアダプター（出力側）として、
    ドメインモデルの永続化を担当する。
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, job: Job) -> None:
        """ジョブを保存する。既存なら UPDATE、新規なら INSERT を行う。"""
        row = await self._session.get(JobRow, str(job.id))
        if row is None:
            row = JobRow(
                id=str(job.id),
                status=job.status.value,
                duration_seconds=job.job_type.duration_seconds,
                notification_channel=job.notification_channel.value,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                result_message=job.result.message if job.result else None,
                result_error=job.result.error if job.result else None,
                discord_thread_id=job.discord_thread_id,
            )
            self._session.add(row)
        else:
            row.status = job.status.value
            row.started_at = job.started_at
            row.completed_at = job.completed_at
            row.result_message = job.result.message if job.result else None
            row.result_error = job.result.error if job.result else None
            row.discord_thread_id = job.discord_thread_id
        await self._session.commit()

    async def find_by_id(self, job_id: JobId) -> Job | None:
        """指定された ID のジョブを取得する。見つからなければ None。"""
        row = await self._session.get(JobRow, str(job_id))
        if row is None:
            return None
        return self._to_domain(row)

    async def find_all(self) -> list[Job]:
        """全ジョブを作成日時の降順で取得する。"""
        result = await self._session.execute(
            select(JobRow).order_by(JobRow.created_at.desc())
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(row: JobRow) -> Job:
        """ORM モデル（JobRow）をドメインモデル（Job）に変換する。"""
        result = None
        if row.result_message is not None:
            result = JobResult(message=row.result_message, error=row.result_error)
        return Job(
            id=JobId(row.id),
            status=JobStatus(row.status),
            job_type=JobType(duration_seconds=row.duration_seconds),
            notification_channel=NotificationChannel(row.notification_channel),
            created_at=row.created_at,
            started_at=row.started_at,
            completed_at=row.completed_at,
            result=result,
            discord_thread_id=row.discord_thread_id,
        )
