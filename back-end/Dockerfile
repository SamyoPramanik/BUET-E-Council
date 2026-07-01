FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

# Enable bytecode compilation to save memory footprint at runtime
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app

# Copy ONLY the package configuration files first
COPY pyproject.toml uv.lock ./

# Install dependencies strictly matching the lockfile
RUN uv sync --frozen --no-install-project --no-dev

# Copy the actual backend source code
COPY . .

EXPOSE 8000

# Streamlined: Boot up Uvicorn directly without the script execution
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]