FROM python:3.12-slim-bookworm

RUN apt update

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install the project with intermediate layers
ADD .dockerignore .

# First, install the dependencies
COPY pyproject.toml uv.lock /
RUN mkdir -p /app

RUN uv sync --frozen --no-install-project

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --compile-bytecode

# Then, install the rest of the project
WORKDIR /app
COPY ./src /app
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
CMD ["uv", "run", "uvicorn", "app:fastapi_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]