import logging

from pydantic import BaseModel
import httpx

from db import RepoInfo


class SearchResult(BaseModel):
    total_count: int
    items: list[RepoInfo]


class GHFetcher:
    def __init__(self, gh_token: str, per_page: int = 100) -> None:
        self.per_page = per_page
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
                    "per_page": self.per_page,
                    "page": page,
                },
            )
            result = SearchResult(**response.json())
            logging.info(f"Считал страницу {page} из {result.total_count}")
            return result.items

        except Exception as e:
            logging.info(f"Ошибка при считывании страницы {page}: {e}")
            return []
