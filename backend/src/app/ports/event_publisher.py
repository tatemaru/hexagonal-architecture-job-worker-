"""イベントパブリッシャーのポート定義。

ヘキサゴナルアーキテクチャにおけるセカンダリポート（出力側）。
ドメインイベントをプロセス外に配信するためのインターフェースを定義する。
具体的な実装（Redis Pub/Sub 等）はアダプター層で提供される。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.events.job_events import DomainEvent


class EventPublisher(ABC):
    """ドメインイベントの配信を担う抽象パブリッシャー。

    ユースケース層はこのインターフェースを通じてイベントを配信し、
    具体的なメッセージング技術（Redis Pub/Sub 等）には依存しない。
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """ドメインイベントを配信する。"""
        ...
