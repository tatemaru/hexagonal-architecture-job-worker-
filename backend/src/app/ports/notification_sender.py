"""通知送信ポートの定義。

ヘキサゴナルアーキテクチャにおけるセカンダリポート（出力側）。
ジョブ完了・失敗時の外部通知を送信するためのインターフェースを定義する。
具体的な実装（Email、Discord 等）はアダプター層で提供される。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.job import Job


class NotificationSender(ABC):
    """通知送信を担う抽象ポート。

    ユースケース層・ワーカーはこのインターフェースを通じて通知を送信し、
    具体的な通知技術（SMTP、Discord Webhook 等）には依存しない。
    """

    @abstractmethod
    async def send(self, job: Job) -> str | None:
        """ジョブの状態に基づいて通知を送信する。

        Returns:
            通知先のスレッドIDなど、後続通知に必要な識別子。不要な場合は None。
        """
        ...
