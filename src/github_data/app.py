import logging
import asyncio

from db import DataBase
from gh_fetcher import GHFetcher

#
DEBUG = True

# Ваш GitHub токен
GITHUB_TOKEN = "token"

# Количество репозиториев для обработки
MAX_REPOS = 200


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


class App:
    def __init__(self, db: DataBase, fetcher: GHFetcher) -> None:
        self.db = db
        self.fetcher = fetcher

    async def fetch_and_save_page(self, page: int) -> None:
        infos = await self.fetcher.fetch_repos_page(page)
        if DEBUG:
            for info in infos:
                print(info)
        await self.db.add_repo_info(infos)

    async def fetch_and_save_pages(self, pages: int) -> None:
        pages = min(pages, get_request_count())
        result_tasks = [self.fetch_and_save_page(page) for page in range(pages)]
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
    db = DataBase()
    await db.init()

    gh_fetcher = GHFetcher(GITHUB_TOKEN)

    app = App(db, gh_fetcher)
    await app.fetch_and_save_pages(1)

    # TODO: Заменить на логгер
    # print("\nСобранные данные о репозиториях:")
    # for repo_data in repositories_data:
    #     print(repo_data)


if __name__ == "__main__":
    asyncio.run(main())
