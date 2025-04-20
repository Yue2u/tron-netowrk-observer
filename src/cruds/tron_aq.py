import pickle
from datetime import timedelta

from redis.asyncio.client import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tron_address_query import TronAddressQuery

INSTANCES_QTY_IN_CACHE = 100
CACHE_TTL = timedelta(seconds=60 * 60)


class TronAddressQueryRepository:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session: AsyncSession = session
        self.redis: Redis = redis

    def _get_cache_key(self):
        return "tron_address_query_key"

    async def insert_record(
        self, address: str, address_data: dict | None = None
    ):
        instance = TronAddressQuery(address=address, address_data=address_data)
        self.session.add(instance)
        await self.session.commit()

        cached_data = await self.redis.get(self._get_cache_key())
        if cached_data is None:
            cached_data = []
        else:
            cached_data = pickle.loads(cached_data)

        if len(cached_data) + 1 > INSTANCES_QTY_IN_CACHE:
            cached_data.pop(len(cached_data))
        cached_data.insert(0, instance)
        await self.redis.set(
            self._get_cache_key(), pickle.dumps(cached_data), ex=CACHE_TTL
        )
        return instance

    async def get_paginated(self, page_size: int = 100, page_number: int = 1):
        if page_number <= 0 or page_size <= 0:
            return []
        if page_number == 1 and page_size <= INSTANCES_QTY_IN_CACHE:
            cached = await self.redis.get(self._get_cache_key())
            if cached is None:
                return []
            return pickle.loads(cached)[:page_size]
        stmt = (
            select(TronAddressQuery)
            .order_by(TronAddressQuery.created_at.desc())
            .offset((page_number - 1) * page_size)
            .limit(page_size)
        )
        taqs = (await self.session.scalars(stmt)).all()
        return taqs
