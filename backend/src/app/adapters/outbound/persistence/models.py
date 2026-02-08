"""SQLAlchemy テーブルモデル定義。

PostgreSQL の jobs テーブルに対応する ORM モデル。
ドメインモデル（Job 集約）とは独立しており、
PostgresJobRepository 内でドメインモデルとの変換を行う。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy の宣言的基底クラス。"""

    pass


class JobRow(Base):
    """jobs テーブルの ORM モデル。

    ドメインの Job 集約をフラットなカラム構造に変換して永続化する。

    Attributes:
        id: ジョブ ID（UUID 文字列）。
        status: ジョブのステータス文字列（PENDING, RUNNING 等）。
        duration_seconds: ダミージョブの実行秒数。
        notification_channel: 通知チャネル（NONE, EMAIL, DISCORD）。
        created_at: 作成日時。
        started_at: 実行開始日時。
        completed_at: 完了（失敗・キャンセル含む）日時。
        result_message: 実行結果メッセージ。
        result_error: エラー情報（失敗時のみ）。
    """

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    notification_channel: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="NONE"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    result_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    discord_thread_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
