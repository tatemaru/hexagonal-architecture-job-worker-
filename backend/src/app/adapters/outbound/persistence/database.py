"""データベース接続設定。

async SQLAlchemy + asyncpg による PostgreSQL への非同期接続を管理する。
環境変数 DATABASE_URL から接続先を取得する。
"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/jobworker",
)

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI の Depends で使用するセッションファクトリ。

    リクエストごとに新しいセッションを生成し、終了時に自動クローズする。
    """
    async with async_session() as session:
        yield session
