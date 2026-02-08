"""ドメインイベントの定義。

Job 集約の状態遷移時に発行されるイベントを定義する。
これらのイベントは Redis Pub/Sub を通じてプロセス間で配信され、
ワーカーや SSE エンドポイントがリアクションするトリガーとなる。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import NewType

JobId = NewType("JobId", uuid.UUID)


@dataclass(frozen=True)
class DomainEvent:
    """全ドメインイベントの基底クラス。

    Attributes:
        job_id: イベントの対象となるジョブの識別子。
        timestamp: イベントが発生した日時（UTC）。
    """

    job_id: JobId
    timestamp: datetime

    @property
    def event_type(self) -> str:
        """イベント種別名を返す（クラス名をそのまま使用）。"""
        return self.__class__.__name__


@dataclass(frozen=True)
class JobCreated(DomainEvent):
    """ジョブが作成され、PENDING 状態になったときに発行される。"""

    pass


@dataclass(frozen=True)
class JobStarted(DomainEvent):
    """ワーカーがジョブの実行を開始し、RUNNING 状態になったときに発行される。"""

    pass


@dataclass(frozen=True)
class JobCompleted(DomainEvent):
    """ジョブが正常に完了し、COMPLETED 状態になったときに発行される。"""

    pass


@dataclass(frozen=True)
class JobFailed(DomainEvent):
    """ジョブの実行が失敗し、FAILED 状態になったときに発行される。"""

    pass


@dataclass(frozen=True)
class JobCancelled(DomainEvent):
    """ユーザーがジョブをキャンセルし、CANCELLED 状態になったときに発行される。"""

    pass
