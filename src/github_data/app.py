import logging
import asyncio
import sys
import random
from datetime import datetime

from db import DataBase
from gh_fetcher import GHFetcher, APIRateException
from token_provider import TokenProvider

# Хранилище
DB_NAME = "data.db"
DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}"

#
DEBUG = True

PATH_TO_TOKENS = sys.argv[1]

# Количество репозиториев для обработки
# 1000 - max
MAX_REPOS = 1000

TOKEN_PROVIDER = TokenProvider(PATH_TO_TOKENS)


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


class App:
    def __init__(self, db: DataBase, fetcher: GHFetcher) -> None:
        self.__db = db
        self.__fetcher = fetcher

    def __update_fetcher_token(self) -> None:
        self.__fetcher.token = TOKEN_PROVIDER.get_token()

    async def fetch_and_save_pages(self, pages: int) -> None:
        result_tasks = [
            self.fetch_and_save_page(page + 1) for page in range(pages)
        ]

        await asyncio.gather(*result_tasks)

    async def fetch_and_save_page(self, page: int) -> None:
        try:
            logging.info(f"Токен доступа: {self.__fetcher.token.value}")

            infos = await self.__fetcher.fetch_repos_page(page, self.__generate_query())
            await self.__db.add_repo_info(infos)

            if DEBUG:
                counter = 1
                for info in infos:
                    logging.info(f"{page}:{counter} Сохранен репозиторий {info}")
                    counter += 1

        except APIRateException:
            logging.error(
                f"Достигнут лимит запросов на странице {page}. Получение нового токена и перезапуск"
            )

            self.__fetcher.token.expired_at = datetime.now()
            self.__fetcher.token = TOKEN_PROVIDER.get_token()

            await self.fetch_and_save_pages(page)

            logging.error(
                f"Токен обновлен: {self.__fetcher.token.value}"
            )

        except Exception as e:
            logging.error(
                f"Ошибка обработки страницы {page}, {e}"
            )

    @staticmethod
    def __generate_query(year: int = 2023, day: int = 1):
        month = random.randint(1, 13)

        date_from = datetime(year, month, day)
        date_to = datetime(year, month + 3, day)

        return f"created:>{date_from} created:<{date_to}"


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

    gh_fetcher = GHFetcher(TOKEN_PROVIDER.get_token())

    app = App(db, gh_fetcher)
    # Кол-во страницы высчитывается на основе кол-ва запрашиваемых репозиториев
    await app.fetch_and_save_pages(get_request_count())


if __name__ == "__main__":
    asyncio.run(main())
