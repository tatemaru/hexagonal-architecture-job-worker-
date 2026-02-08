"""REST API エンドポイント（プライマリアダプター）。

ヘキサゴナルアーキテクチャのプライマリアダプター（入力側）として、
HTTP リクエストを受け取り、ユースケースを呼び出してレスポンスを返す。
ドメイン例外は適切な HTTP ステータスコードに変換される。
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.messaging.redis_event_publisher import RedisEventPublisher
from app.adapters.outbound.persistence.database import get_session
from app.adapters.outbound.persistence.postgres_job_repository import (
    PostgresJobRepository,
)
from app.domain.exceptions import InvalidStatusTransitionError, JobNotFoundError
from app.domain.models.job import Job, JobId
from app.domain.models.notification import NotificationChannel
from app.usecases.cancel_job import CancelJobUseCase
from app.usecases.create_job import CreateJobUseCase
from app.usecases.get_job import GetJobUseCase
from app.usecases.list_jobs import ListJobsUseCase

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# --- リクエスト / レスポンスのスキーマ ---


class CreateJobRequest(BaseModel):
    """ジョブ作成リクエスト。

    Attributes:
        duration_seconds: ダミージョブの実行秒数。
        notification_channel: 通知チャネル（none / email / discord）。
    """

    duration_seconds: int
    notification_channel: str = "none"


class JobResponse(BaseModel):
    """ジョブ情報のレスポンス。

    ドメインモデル（Job）を API クライアント向けにフラットに変換した形式。
    """

    id: str
    status: str
    duration_seconds: int
    notification_channel: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result_message: str | None
    result_error: str | None


def _to_response(job: Job) -> JobResponse:
    """ドメインモデル（Job）を API レスポンス形式に変換する。"""
    return JobResponse(
        id=str(job.id),
        status=job.status.value,
        duration_seconds=job.job_type.duration_seconds,
        notification_channel=job.notification_channel.value.lower(),
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result_message=job.result.message if job.result else None,
        result_error=job.result.error if job.result else None,
    )


# --- エンドポイント ---


@router.post("", status_code=status.HTTP_201_CREATED, response_model=JobResponse)
async def create_job(
    body: CreateJobRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    """POST /api/jobs - 新しいジョブを作成する。"""
    repo = PostgresJobRepository(session)
    publisher = RedisEventPublisher(request.app.state.redis)
    usecase = CreateJobUseCase(repo, publisher)
    channel = NotificationChannel(body.notification_channel.upper())
    job = await usecase.execute(body.duration_seconds, notification_channel=channel)
    return _to_response(job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    session: AsyncSession = Depends(get_session),
) -> list[JobResponse]:
    """GET /api/jobs - ジョブ一覧を取得する。"""
    repo = PostgresJobRepository(session)
    usecase = ListJobsUseCase(repo)
    jobs = await usecase.execute()
    return [_to_response(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    """GET /api/jobs/{job_id} - ジョブの詳細を取得する。"""
    repo = PostgresJobRepository(session)
    usecase = GetJobUseCase(repo)
    try:
        job = await usecase.execute(JobId(uuid.UUID(job_id)))
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    """POST /api/jobs/{job_id}/cancel - ジョブをキャンセルする。

    PENDING または RUNNING 状態のジョブのみキャンセル可能。
    完了済みのジョブをキャンセルしようとすると 400 エラーを返す。
    """
    repo = PostgresJobRepository(session)
    publisher = RedisEventPublisher(request.app.state.redis)
    usecase = CancelJobUseCase(repo, publisher)
    try:
        job = await usecase.execute(JobId(uuid.UUID(job_id)))
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(job)
