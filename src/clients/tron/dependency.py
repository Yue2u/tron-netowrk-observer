from contextlib import contextmanager
from typing import Annotated

import httpx
from fastapi import Depends

from common.httpx import get_httpx_clint

from .client import TronClient


def get_tron_client(
    httpx_client: Annotated[httpx.AsyncClient, Depends(get_httpx_clint)],
):
    yield TronClient(httpx_client)
