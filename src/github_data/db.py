import uuid
from datetime import datetime
import pandas as pd

from sqlmodel import SQLModel, Field, select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class RepoInfo(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id: int
    full_name: str
    language: str | None
    created_at: datetime
    pushed_at: datetime


class DataBase:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def add_repo_info(self, infos: list[RepoInfo]) -> None:
        async with self.session() as session:
            async with session.begin():
                infos = [RepoInfo.validate(info) for info in infos]
                session.add_all(infos)
                await session.commit()

    async def max_date(self) -> datetime:
        async with self.session() as session:
            async with session.begin():
                s = select(func.max(RepoInfo.created_at))
                res = await session.execute(s)
                return res.scalar()

    async def min_date(self) -> datetime:
        async with self.session() as session:
            async with session.begin():
                s = select(func.min(RepoInfo.created_at))
                res = await session.execute(s)
                return res.scalar()

    async def get_counts(
        self,
        query_by=RepoInfo.created_at,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> pd.DataFrame:
        if date_from is None:
            date_from = await self.min_date()

        if date_to is None:
            date_to = await self.max_date()

        async with self.session() as session:
            async with session.begin():
                s = (
                    select(RepoInfo.language, func.count())
                    .where(RepoInfo.language.isnot(None))
                    .where(query_by.between(date_from, date_to))
                    .group_by(RepoInfo.language)
                )
                res = await session.execute(s)
                df = pd.DataFrame(res.all(), columns=["language", "count"])
                df.set_index("language", inplace=True)
                return df
