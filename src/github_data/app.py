import logging
import asyncio

from pydantic import BaseModel
import httpx

from db import RepoInfo

# Ваш GitHub токен
GITHUB_TOKEN = "token"

# Количество репозиториев для обработки
MAX_REPOS = 200


class SearchResult(BaseModel):
    items: list[RepoInfo]


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


class GHFetcher:
    def __init__(self):
        self.httpx_client = httpx.AsyncClient()

    async def fetch_repos_page(self, page: int) -> list[RepoInfo]:
        # Вычитываем страницы (1 страница содержит 100 репозиториев)
        try:
            response = await self.httpx_client.get(
                "https://api.github.com/search/repositories?q=''",
                params={
                    "q": f"stars:>{100}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 100,
                    "page": page,
                },
            )
            result = SearchResult(**response.json())
            return result.items

        except Exception as e:
            logging.info(f"Ошибка при считывании страницы {page}: {e}")
            return []

    # Получение репозиториев
    async def fetch_repos(self, pages: int) -> None:
        pages = min(pages, get_request_count())
        result_tasks = [self.fetch_repos_page(i) for i in range(pages)]
        results = await asyncio.gather(*result_tasks)
        infos = [info for result in results for info in result]
        for info in infos:
            print(info)


# for repo in repos:
#     try:
#         if repo.size > 500:
#             logging.info(
#                 f"Превышен размер файла {repo.full_name}, размер {repo.size}"
#             )
#             pass
#         if repo.language is None:
#             logging.info(f"Язык в репозитории {repo.full_name} - None")
#             pass
#         repo_data = {
#             "name": repo.full_name,
#             "stars": repo.stargazers_count,
#             "language": repo.language,
#             # "lines_of_code": get_lines_of_code(repo),
#         }
#         repositories_data.append(repo_data)
#         logging.info(f"Добавлен репозиторий: {repo_data}")

# def generate_random_stars_range():
#     start = random.randint(0, 1000)
#     end = start + random.randint(50, 500)
#     return f"stars:{start}..{end}"


# Подсчет строк кода в репозитории
def get_lines_of_code(repo) -> int:
    try:
        lines_of_code = 0
        contents = repo.get_contents("")

        while contents:
            file_content = contents.pop(0)

            if file_content.type == "file":
                lines_of_code += len(file_content.decoded_content.splitlines())
            elif file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))

        return lines_of_code

    except Exception as e:
        logging.info(f"Ошибка подсчета строк кода в {repo.full_name}: {e}")
        return 0


async def main() -> None:
    # Логгер
    logging.basicConfig(
        level=logging.INFO,
        filename="app_log.log",
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s%(levelname)s %(message)s",
    )

    # Хранилище данных о репозиториях
    gh_fetcher = GHFetcher()
    await gh_fetcher.fetch_repos(1)

    # TODO: Заменить на логгер
    # print("\nСобранные данные о репозиториях:")
    # for repo_data in repositories_data:
    #     print(repo_data)


if __name__ == "__main__":
    asyncio.run(main())
