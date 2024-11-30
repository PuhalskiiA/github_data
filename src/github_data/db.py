from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"


class RepoInfo(SQLModel, table=True):
    id: int = Field(primary_key=True)
    full_name: str
    language: str | None
    created_at: datetime
    pushed_at: datetime


class DataBase:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite://", echo=False)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def add_repo_info(self, infos: list[RepoInfo]) -> None:
        async with self.session() as session:
            async with session.begin():
                session.add_all(infos)