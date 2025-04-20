from typing import Annotated

from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from common.db import get_session
from common.redis import Redis, get_redis
from models.base import Base

from .tron_aq import TronAddressQueryRepository


class UoW:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session: AsyncSession = session
        self.redis: Redis = redis

        self.tron_aq = TronAddressQueryRepository(session, redis)

    def add(self, instance: Base):
        self.session.add(instance)

    async def delete(self, instance: Base):
        await self.session.delete(instance)

    async def merge(self, instance: Base) -> Base:
        return await self.session.merge(instance)

    async def commit(self):
        await self.session.commit()

    async def refresh(self, instance: Base):
        await self.session.refresh(instance)


async def get_uow(
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    yield UoW(session, redis)
