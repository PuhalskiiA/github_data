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

    async def fetch_repos_page(self) -> list[RepoInfo]:
        # Вычитываем страницы (1 страница содержит 100 репозиториев)
        try:
            response = await self.httpx_client.get(
                "https://api.github.com/search/repositories?q=''",
                params={
                    "q": f"stars:>{100}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 100,
                },
            )
            result = SearchResult(**response.json())
            return result.items

        except Exception as e:
            logging.info(f"Ошибка при считывании страницы: {e}")
            return []
