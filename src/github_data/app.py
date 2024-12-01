import logging
import asyncio
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

# Выгружить репозитории за последние n лет
FETCH_YEARS = 1


class App:
    def __init__(self, db: DataBase, fetcher: GHFetcher) -> None:
        self.__db = db
        self.__fetcher = fetcher

    def __update_fetcher_token(self) -> None:
        self.__fetcher.token = TOKEN_PROVIDER.get_token()

    def __get_request_count(self) -> int:
        per_page = self.__fetcher.per_page
        if MAX_REPOS % per_page == 0:
            return MAX_REPOS // per_page
        else:
            return MAX_REPOS // per_page + 1

    @staticmethod
    def __get_query(date_from: datetime, date_to: datetime) -> str:
        fmt_str = "%Y-%m-%d"
        date_from_str = date_from.strftime(fmt_str)
        date_to_str = date_to.strftime(fmt_str)
        return f"created:>={date_from_str} created:<{date_to_str}"

    async def search_and_save(self, query: str) -> None:
        for page in range(1, self.__get_request_count() + 1):
            await self.search_and_save_page(query, page)

    async def fetch_and_save_repos(self) -> None:
        tasks = []
        end_date = datetime.now()
        current_date = end_date - relativedelta(years=FETCH_YEARS)
        while current_date < end_date:
            next_date = current_date + relativedelta(months=1)
            query = self.__get_query(current_date, next_date)
            tasks.append(self.search_and_save(query))
            current_date = next_date
        await asyncio.gather(*tasks)

    async def search_and_save_page(self, query: str, page: int) -> None:
        while True:
            try:
                logging.info(f"Токен доступа: {self.__fetcher.token.value}")

                infos = await self.__fetcher.fetch_repos_page(page, query)
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

                logging.error(f"Токен обновлен: {self.__fetcher.token.value}")
                continue

            except Exception as e:
                logging.error(f"Ошибка обработки страницы {page}, {e}")

            break


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
    await app.fetch_and_save_repos()


if __name__ == "__main__":
    asyncio.run(main())
