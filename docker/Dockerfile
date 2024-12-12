FROM python:3.13.1

WORKDIR /app

RUN pip install uv

# COPY docker/entry.sh .

COPY pyproject.toml uv.lock .

RUN uv sync

COPY docker/entry.sh .

ENTRYPOINT ["./entry.sh"]
