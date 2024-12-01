import base64
import logging

from pydantic import BaseModel
import httpx

from db import RepoInfo
from token_provider import Token


class SearchResult(BaseModel):
    total_count: int
    items: list[RepoInfo]


class APIRateException(Exception):
    pass


class GHFetcher:
    def __init__(self, token: Token, per_page: int = 100) -> None:
        self.__per_page = per_page
        self.__token = token
        self.__httpx_client = httpx.AsyncClient()

    @property
    def token(self) -> Token:
        return self.__token

    @token.setter
    def token(self, token: Token) -> None:
        self.__token = token

    async def fetch_repos_page(self, page: int, query: str) -> list[RepoInfo]:
        headers = {
            "Authorization": f"Bearer {self.token.value}",
        }
        params = httpx.QueryParams(
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": self.__per_page,
                "page": page,
            }
        )

        logging.info(f"Параметры запроса: {params}")

        response = await self.__httpx_client.get(
            "https://api.github.com/search/repositories", params=params, headers=headers
        )

        if response.status_code == httpx.codes.FORBIDDEN:
            raise APIRateException()

        result = SearchResult(**response.json())
        logging.info(f"Считал страницу {page} из {result.total_count}")

        return result.items
