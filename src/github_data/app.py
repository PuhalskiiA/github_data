import logging
import asyncio

from db import DataBase
from gh_fetcher import GHFetcher

# Хранилище
DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"

#
DEBUG = True

# Ваш GitHub токен
GITHUB_TOKEN = "token"

# Количество репозиториев для обработки
MAX_REPOS = 500


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


class App:
    def __init__(self, db: DataBase, fetcher: GHFetcher) -> None:
        self.db = db
        self.fetcher = fetcher

    async def fetch_and_save_page(self) -> None:
        infos = await self.fetcher.fetch_repos_page()
        await self.db.add_repo_info(infos)

        if DEBUG:
            for info in infos:
                logging.info(f"Сохранен репозиторий {info}")

    async def fetch_and_save_pages(self) -> None:
        result_tasks = [self.fetch_and_save_page() for _ in range(get_request_count())]
        await asyncio.gather(*result_tasks)


async def main() -> None:
    # Логгер
    logging.basicConfig(
        level=logging.INFO,
        filename="app_log.log",
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s%(levelname)s %(message)s",
    )

    # Инициализация базы данных
    db = DataBase(DB_URL)
    await db.init()

    gh_fetcher = GHFetcher(GITHUB_TOKEN)

    app = App(db, gh_fetcher)
    await app.fetch_and_save_pages()


if __name__ == "__main__":
    asyncio.run(main())
