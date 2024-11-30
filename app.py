import logging
from github import Github

# Ваш GitHub токен
GITHUB_TOKEN = "Сюда токен"

# Инициализация клиента GitHub
g = Github(GITHUB_TOKEN)

# Количество репозиториев для обработки
MAX_REPOS = 1000

# Хранилище данных о репозиториях
repositories_data = []

# Логгер
logging.basicConfig(level=logging.INFO, filename="app_log.log", filemode="w", encoding="utf-8",
                    format="%(asctime)s%(levelname)s %(message)s")


# Получение репозиториев
def fetch_repositories():
    repos = g.search_repositories(
        query="stars:>1",
        sort="stars",
        order="desc"
    )

    for repo in repos[:MAX_REPOS]:
        try:
            repo_data = {
                "name": repo.full_name,
                "stars": repo.stargazers_count,
                "language": repo.language,
                "lines_of_code": get_lines_of_code(repo),
            }

            repositories_data.append(repo_data)

            logging.info(f'Добавлен репозиторий: {repo_data}')

        except Exception as e:

            logging.info(f'Ошибка при обработке {repo.full_name}: {e}')


# Подсчет строк кода в репозитории
def get_lines_of_code(repo):
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
        logging.info(f'Ошибка подсчета строк кода в {repo.full_name}: {e}')
        return 0


def main():
    fetch_repositories()

    # TODO: Заменить на логгер
    print("\nСобранные данные о репозиториях:")
    for repo_data in repositories_data:
        print(repo_data)


if __name__ == "__main__":
    main()