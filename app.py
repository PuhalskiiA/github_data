import logging

# import random

from pydantic import BaseModel
import httpx


class RepoInfo(BaseModel):
    full_name: str
    language: str | None
    contents_url: str


class SearchResult(BaseModel):
    items: list[RepoInfo]


# Ваш GitHub токен
GITHUB_TOKEN = "token"

# Количество репозиториев для обработки
MAX_REPOS = 200


# Получение репозиториев
def fetch_repos_page(page: int) -> SearchResult:
    # Вычитываем страницы (1 страница содержит 100 репозиториев)
    try:
        response = httpx.get(
            "https://api.github.com/search/repositories?q=''",
            params={
                "q": "stars>100",
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": page,
            },
        )
        return SearchResult(**response.json())
    except Exception as e:
        logging.info(f"Ошибка при считывании страницы {page}: {e}")


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


def get_request_count() -> int:
    if MAX_REPOS % 100 == 0:
        return MAX_REPOS // 100
    else:
        return MAX_REPOS // 100 + 1


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


def fetch_repos(pages: int) -> None:
    pages = min(pages, get_request_count())
    for i in range(pages):
        search_result = fetch_repos_page(i)
        print(search_result)


def main() -> None:
    # Логгер
    logging.basicConfig(
        level=logging.INFO,
        filename="app_log.log",
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s%(levelname)s %(message)s",
    )

    # Хранилище данных о репозиториях
    fetch_repos(1)

    # TODO: Заменить на логгер
    # print("\nСобранные данные о репозиториях:")
    # for repo_data in repositories_data:
    #     print(repo_data)


if __name__ == "__main__":
    main()
