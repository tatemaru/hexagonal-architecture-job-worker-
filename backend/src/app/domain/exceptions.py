"""ドメイン例外の定義。

ドメインルール違反時にスローされる例外を定義する。
これらの例外はドメイン層の不変条件を表現しており、
アダプター層で適切な HTTP レスポンス等に変換される。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.models.job import JobStatus


class DomainError(Exception):
    """全ドメイン例外の基底クラス。"""

    pass


class InvalidStatusTransitionError(DomainError):
    """ステートマシンで許可されていない状態遷移が試みられた場合にスローされる。

    例: COMPLETED → PENDING への遷移は禁止されている。

    Attributes:
        current: 遷移元のステータス。
        target: 遷移先のステータス。
    """

    def __init__(self, current: JobStatus, target: JobStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(f"Cannot transition from {current.value} to {target.value}")


class JobNotFoundError(DomainError):
    """指定された JobId に対応するジョブが存在しない場合にスローされる。

    Attributes:
        job_id: 見つからなかったジョブの ID 文字列。
    """

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job not found: {job_id}")
