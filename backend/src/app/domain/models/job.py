"""Job 集約ルートと値オブジェクトの定義。

このモジュールはドメイン層の中心であり、外部ライブラリに一切依存しない。
ジョブのライフサイクル（状態遷移）ルールとドメインイベントの発行を担う。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import NewType

from app.domain.events.job_events import (
    DomainEvent,
    JobCancelled,
    JobCompleted,
    JobCreated,
    JobFailed,
    JobStarted,
)
from app.domain.exceptions import InvalidStatusTransitionError
from app.domain.models.notification import NotificationChannel

# --- 値オブジェクト（Value Objects） ---

JobId = NewType("JobId", uuid.UUID)
"""ジョブの一意識別子。UUID のラッパー型。"""


class JobStatus(Enum):
    """ジョブの状態を表す列挙型。

    ステートマシンの遷移ルールを内部に持ち、
    許可されない遷移を試みると InvalidStatusTransitionError をスローする。

    状態遷移図:
        PENDING  → RUNNING | CANCELLED
        RUNNING  → COMPLETED | FAILED | CANCELLED
        COMPLETED, FAILED, CANCELLED → （遷移不可）
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    _allowed_transitions: dict[JobStatus, set[JobStatus]]

    @staticmethod
    def _get_allowed_transitions() -> dict[JobStatus, set[JobStatus]]:
        """許可される状態遷移の定義を返す。"""
        return {
            JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.CANCELLED},
            JobStatus.RUNNING: {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            },
            JobStatus.COMPLETED: set(),
            JobStatus.FAILED: set(),
            JobStatus.CANCELLED: set(),
        }

    def can_transition_to(self, target: JobStatus) -> bool:
        """指定された状態への遷移が許可されているか判定する。"""
        return target in self._get_allowed_transitions()[self]

    def transition_to(self, target: JobStatus) -> JobStatus:
        """状態遷移を実行する。許可されていない場合は例外をスローする。

        Raises:
            InvalidStatusTransitionError: 遷移が禁止されている場合。
        """
        if not self.can_transition_to(target):
            raise InvalidStatusTransitionError(self, target)
        return target


@dataclass(frozen=True)
class JobType:
    """ジョブの種別を表す値オブジェクト。

    学習用のため、指定秒数 sleep して完了するダミージョブのみ。

    Attributes:
        duration_seconds: ジョブの実行秒数。
    """

    duration_seconds: int


@dataclass(frozen=True)
class JobResult:
    """ジョブの実行結果を表す値オブジェクト。

    Attributes:
        message: 結果メッセージ（正常完了時・異常終了時ともに設定される）。
        error: エラー情報（異常終了時のみ設定される）。
    """

    message: str
    error: str | None = None


# --- 集約ルート（Aggregate Root） ---


@dataclass
class Job:
    """Job 集約ルート。

    ジョブのライフサイクル全体を管理する唯一の集約。
    状態遷移のルール（不変条件）を内部に持ち、
    遷移時にドメインイベントを発行する。

    外部からジョブの状態を変更するには、必ずこの集約のメソッド
    （start, complete, fail, cancel）を通す必要がある。

    Attributes:
        id: ジョブの一意識別子。
        status: 現在のステータス。
        job_type: ジョブの種別（実行秒数）。
        notification_channel: 通知チャネル（NONE / EMAIL / DISCORD）。
        discord_thread_id: Discord フォーラムスレッドID（開始通知で作成されたスレッドへの返信に使用）。
        created_at: ジョブの作成日時。
        started_at: ジョブの実行開始日時。
        completed_at: ジョブの完了（または失敗・キャンセル）日時。
        result: ジョブの実行結果。
        events: 未配信のドメインイベントリスト。
    """

    id: JobId
    status: JobStatus
    job_type: JobType
    notification_channel: NotificationChannel
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: JobResult | None = None
    discord_thread_id: str | None = None
    events: list[DomainEvent] = field(default_factory=list, repr=False)

    @staticmethod
    def create(
        job_type: JobType,
        notification_channel: NotificationChannel = NotificationChannel.NONE,
    ) -> Job:
        """新しいジョブを作成する（ファクトリメソッド）。

        PENDING 状態で生成され、JobCreated イベントが発行される。
        """
        job_id = JobId(uuid.uuid4())
        now = datetime.now(timezone.utc)
        job = Job(
            id=job_id,
            status=JobStatus.PENDING,
            job_type=job_type,
            notification_channel=notification_channel,
            created_at=now,
        )
        job.events.append(JobCreated(job_id=job_id, timestamp=now))
        return job

    def start(self) -> None:
        """ジョブの実行を開始する。PENDING → RUNNING に遷移し、JobStarted を発行する。"""
        self.status = self.status.transition_to(JobStatus.RUNNING)
        self.started_at = datetime.now(timezone.utc)
        self.events.append(JobStarted(job_id=self.id, timestamp=self.started_at))

    def complete(self, result: JobResult) -> None:
        """ジョブを正常完了させる。RUNNING → COMPLETED に遷移し、JobCompleted を発行する。"""
        self.status = self.status.transition_to(JobStatus.COMPLETED)
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
        self.events.append(JobCompleted(job_id=self.id, timestamp=self.completed_at))

    def fail(self, result: JobResult) -> None:
        """ジョブを失敗させる。RUNNING → FAILED に遷移し、JobFailed を発行する。"""
        self.status = self.status.transition_to(JobStatus.FAILED)
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
        self.events.append(JobFailed(job_id=self.id, timestamp=self.completed_at))

    def cancel(self) -> None:
        """ジョブをキャンセルする。PENDING/RUNNING → CANCELLED に遷移し、JobCancelled を発行する。"""
        self.status = self.status.transition_to(JobStatus.CANCELLED)
        self.completed_at = datetime.now(timezone.utc)
        self.events.append(JobCancelled(job_id=self.id, timestamp=self.completed_at))

    def collect_events(self) -> list[DomainEvent]:
        """未配信のドメインイベントを取り出す。取り出し後、内部リストはクリアされる。"""
        events = self.events.copy()
        self.events.clear()
        return events
