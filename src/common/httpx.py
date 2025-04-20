import httpx


# Dependency for override
def get_httpx_clint() -> httpx.AsyncClient:
    raise NotImplementedError()
