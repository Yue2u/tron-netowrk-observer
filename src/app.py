from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from common.httpx import get_httpx_clint
from common.redis import get_redis, redis
from routers.root import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use context manager to automatically close all connections
    # on application shutdown. Also one client per app let us
    # keep http connection open and not to reopen it on every request to tron
    async with httpx.AsyncClient() as httpx_client:
        app.dependency_overrides[get_httpx_clint] = lambda: httpx_client
        app.dependency_overrides[get_redis] = lambda: redis


fastapi_app = FastAPI(title="Tron Network Observer", lifespan=lifespan)
fastapi_app.include_router(router)
