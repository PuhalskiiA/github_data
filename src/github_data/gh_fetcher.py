import logging

from pydantic import BaseModel
import httpx

from db import RepoInfo


class SearchResult(BaseModel):
    total_count: int
    items: list[RepoInfo]


class APIRateException(Exception):
    def __init__(self):
        super()


class GHFetcher:
    def __init__(self, gh_token: str, per_page: int = 100) -> None:
        self.per_page = per_page
        self.gh_token = gh_token
        self.httpx_client = httpx.AsyncClient()
        self.total_count = 0

    def get_total_count(self):
        return self.total_count

    async def fetch_repos_page(self, page: int) -> list[RepoInfo]:
        headers = {
            "Authorization": f"Bearer {self.gh_token}",
        }

        response = await self.httpx_client.get(
            "https://api.github.com/search/repositories?q=''",
            params={
                "q": f"stars:>{100}",
                "sort": "stars",
                "order": "desc",
                "per_page": self.per_page,
                "page": page,
            }, headers=headers,
        )

        if response.status_code == 403:
            raise APIRateException()

        result = SearchResult(**response.json())
        logging.info(f"Считал страницу {page} из {result.total_count}")

        # TODO: Не работает нихуя
        if self.total_count == 0:
            self.total_count = result.total_count

        return result.items
