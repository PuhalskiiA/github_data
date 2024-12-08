import logging
import asyncio

import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta

from db import DataBase
from gh_fetcher import GHFetcher, APIRateException
from token_provider import TokenProvider
from settings import settings


TOKEN_PROVIDER = TokenProvider(settings.path_to_tokens)


class App:
    def __init__(self, db: DataBase, fetcher: GHFetcher) -> None:
        self.__db = db
        self.__fetcher = fetcher
        self.__tqdm: tqdm.tqdm | None = None

    def __get_request_count(self) -> int:
        per_page = self.__fetcher.per_page
        max_repos = settings.max_repos
        if max_repos % per_page == 0:
            return max_repos // per_page
        else:
            return max_repos // per_page + 1

    @staticmethod
    def __get_query(date: datetime) -> str:
        date_str = date.strftime("%Y-%m-%d")
        return f"fork:false created:{date_str}"

    async def search_and_save(self, query: str) -> None:
        for page in range(1, self.__get_request_count() + 1):
            await self.search_and_save_page(query, page)

    async def search_and_save_by_day(self, date: datetime) -> None:
        end_date = date + relativedelta(months=1)
        while date < end_date:
            query = self.__get_query(date)
            await self.search_and_save(query)
            self.__tqdm.update(1)
            date = date + relativedelta(days=1)

    async def fetch_and_save_repos(self) -> None:
        tasks = []
        end_date = datetime.now()
        current_date = end_date - relativedelta(years=settings.fetch_years)
        total_steps = (end_date - current_date).days
        self.__tqdm = tqdm.tqdm(total=total_steps, desc="Fetching")
        while current_date < end_date:
            next_date = current_date + relativedelta(months=1)
            tasks.append(self.search_and_save_by_day(next_date))
            current_date = next_date
        await asyncio.gather(*tasks)
        self.__tqdm.close()

    async def search_and_save_page(self, query: str, page: int) -> None:
        while True:
            try:
                logging.info(f"Токен доступа: {self.__fetcher.token.value}")

                infos = await self.__fetcher.fetch_repos_page(page, query)
                await self.__db.add_repo_info(infos)

                if settings.debug:
                    counter = 1
                    for info in infos:
                        logging.info(f"{page}:{counter} Сохранен репозиторий {info}")
                        counter += 1

            except APIRateException:
                logging.error(
                    f"Достигнут лимит запросов на странице {page}. Получение нового токена и перезапуск"
                )

                self.__fetcher.token.expired_at = datetime.now()
                self.__fetcher.token = await TOKEN_PROVIDER.get_token()

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
    db = DataBase(settings.db_url)
    await db.init()

    gh_fetcher = GHFetcher(await TOKEN_PROVIDER.get_token())

    app = App(db, gh_fetcher)
    # Кол-во страницы высчитывается на основе кол-ва запрашиваемых репозиториев
    await app.fetch_and_save_repos()


if __name__ == "__main__":
    asyncio.run(main())
