# Анализ популярности языков на GitHub

## Инструкции по запуску

Клонируем репозиторий.

```console
git clone https://github.com/PuhalskiiA/github_data
```

Собираем Docker изображение.

```console
cd github_data
docker build -t github_data -f docker/Dockerfile .
```

Создаем `.env` файл, здесь прописываем требуемые значения.
Путь к файлу базы данных и к файлу с токенами GitHub рассматриваются относительно директории `src`.

```console
cp ENV_EXAMPLE .env
```

Запускаем процесс сборки данных с API GitHub.

```console
docker run --rm -it -v ./src:/app/src -v .env:/app/.env github_data:latest save
```

Запускаем анализатор (построение графиков по полученным данным). Результаты помещаются в папку `src`.

```console
docker run --rm -it -v ./src:/app/src -v .env:/app/.env github_data:latest analyze
```
