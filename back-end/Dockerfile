FROM ghcr.io/astral-sh/uv:python3.12-alpine

RUN apk add --no-cache busybox-extras

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uv run python scripts/run_seed.py && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]