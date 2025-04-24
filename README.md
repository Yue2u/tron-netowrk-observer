To run project locally

1. docker create network tron-network
2. docker compose up --build

For production use need to extend docker-compose and connect reverse-proxy like traeffik or nginx

To run tests
docker exec -it <container name> uv run pytest

For local development
1. Install astral-uv
2. uv sync
3. For adding a lib uv add lib_name==lib_version