"""ジョブリポジトリのポート定義。

ヘキサゴナルアーキテクチャにおけるセカンダリポート（出力側）。
ドメイン層がデータの永続化を行うためのインターフェースを定義する。
具体的な実装（PostgreSQL 等）はアダプター層で提供される。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.job import Job, JobId


class JobRepository(ABC):
    """ジョブの永続化を担う抽象リポジトリ。

    ドメイン層とユースケース層はこのインターフェースにのみ依存し、
    具体的なデータベース技術には依存しない（依存性逆転の原則）。
    """

    @abstractmethod
    async def save(self, job: Job) -> None:
        """ジョブを保存する。新規の場合は INSERT、既存の場合は UPDATE を行う。"""
        ...

    @abstractmethod
    async def find_by_id(self, job_id: JobId) -> Job | None:
        """指定された ID のジョブを取得する。見つからない場合は None を返す。"""
        ...

    @abstractmethod
    async def find_all(self) -> list[Job]:
        """全ジョブを作成日時の降順で取得する。"""
        ...
