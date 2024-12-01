import logging
import asyncio
import sys
import random
from datetime import datetime

from db import DataBase
from gh_fetcher import GHFetcher
from gh_fetcher import APIRateException
from token_provider import TokenProvider

# Хранилище
DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"

#
DEBUG = True

PATH_TO_TOKENS = sys.argv[1]

# Количество репозиториев для обработки
MAX_REPOS = 1000

TOKEN_PROVIDER = TokenProvider(PATH_TO_TOKENS)


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


class App:
    def __init__(self, db: DataBase) -> None:
        self.db = db
        self.__update_fetcher()

    def __update_fetcher(self) -> None:
        self.fetcher = self.__get_fetcher()

    @staticmethod
    def __get_fetcher():
        return GHFetcher(TOKEN_PROVIDER.get_token().get_value())

    async def fetch_and_save_pages(self, pages: int) -> None:
        result_tasks = [self.fetch_and_save_page(self.__get_page(self.fetcher)) for _ in range(pages)]
        await asyncio.gather(*result_tasks)

    @staticmethod
    def __get_page(fetcher: GHFetcher) -> int:
        if fetcher.get_total_count() == 0:
            return 1
        else:
            return random.randint(2, fetcher.get_total_count() + 1)

    async def fetch_and_save_page(self, page: int) -> None:
        try:
            infos = await self.fetcher.fetch_repos_page(page)
            await self.db.add_repo_info(infos)

            if DEBUG:
                counter = 1
                for info in infos:
                    logging.info(f"{counter} Сохранен репозиторий {info}")
                    counter += 1

        except APIRateException:
            logging.error(f"Достигнут лимит запросов на странице {page}. Получение нового токена и перезапуск")

            self.fetcher.gh_token.set_expired_at(datetime.now())
            self.__update_fetcher()

            await self.fetcher.fetch_repos_page(page)


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

    app = App(db)
    # Кол-во страницы высчитывается на основе кол-ва запрашиваемых репозиториев
    await app.fetch_and_save_pages(get_request_count())


if __name__ == "__main__":
    asyncio.run(main())
