import logging

from pydantic import BaseModel
import httpx

from db import RepoInfo


class SearchResult(BaseModel):
    items: list[RepoInfo]


class GHFetcher:
    def __init__(self, gh_token: str) -> None:
        self.gh_token = gh_token
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
