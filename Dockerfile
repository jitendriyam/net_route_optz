FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv==0.5.18

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY tests ./tests

ENV PATH="/app/.venv/bin:$PATH"

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
