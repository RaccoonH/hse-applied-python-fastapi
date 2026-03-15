import asyncio
from sqlalchemy import delete, update
from sqlalchemy.sql.functions import coalesce
from .models import Link
import datetime
from .cache import remove_link, redis_lock, REDIS_GET_TAG, REDIS_COUNTER_TAG, REDIS_USE_TIME_TAG
from sqlalchemy.ext.asyncio import AsyncSession
import json


async def watch_event_iterate(session: AsyncSession, redis_client):
    async with redis_lock(redis_client):
        now = datetime.datetime.now(datetime.timezone.utc)
        await cleanup_expired_links(session, redis_client, now)
        moved = await move_cache_to_database(session, redis_client, now)
        await remove_unused_link(session, redis_client, now, moved)


CLEANUP_INTERVAL_SEC = 60
LAST_CLEANUP_TIME = datetime.datetime.now(datetime.timezone.utc)


async def cleanup_expired_links(session: AsyncSession, redis_client, now):
    global LAST_CLEANUP_TIME

    diff = now - LAST_CLEANUP_TIME
    if diff.total_seconds() >= CLEANUP_INTERVAL_SEC:
        LAST_CLEANUP_TIME = now
        query = delete(Link).where(Link.expires_at <= now).returning(Link.code)
        res = await session.execute(query)
        res = res.scalars().all()

        if len(res) > 0:
            coroutine_list = []
            for i in res:
                coroutine_list.append(remove_link(i, redis_client))
            await asyncio.gather(*coroutine_list)
            await session.commit()


CACHE_TO_DATABASE_INTERVAL_SEC = 60 * 5
LAST_MOVE_TIME = datetime.datetime.now(datetime.timezone.utc)


async def move_cache_to_database(session: AsyncSession, redis_client, now):
    global LAST_MOVE_TIME

    diff = now - LAST_MOVE_TIME
    if diff.total_seconds() >= CACHE_TO_DATABASE_INTERVAL_SEC:
        LAST_MOVE_TIME = now
        async for key in redis_client.scan_iter(match=f"{REDIS_GET_TAG}*"):
            value = await redis_client.get(key)
            value = json.loads(value)

            update_values = {
                "counter": value[REDIS_COUNTER_TAG],
                "last_use_time": datetime.datetime.fromisoformat(value[REDIS_USE_TIME_TAG]),
            }
            query = update(Link).where(Link.code == key.decode('utf-8')[len(REDIS_GET_TAG):]).values(update_values)
            await session.execute(query)
            await redis_client.delete(key)

        await session.commit()
        return True
    return False


REMOVE_UNUSED_LINK_INTERVAL_SEC = 24 * 60 * 60
LAST_REMOVE_UNUSED_LINK_TIME = datetime.datetime.now(datetime.timezone.utc)


async def remove_unused_link(session: AsyncSession, redis_client, now, moved_cache):
    global LAST_REMOVE_UNUSED_LINK_TIME

    diff = now - LAST_REMOVE_UNUSED_LINK_TIME

    if diff.total_seconds() >= REMOVE_UNUSED_LINK_INTERVAL_SEC:
        if moved_cache is False:
            await move_cache_to_database(session, redis_client, now)
        LAST_REMOVE_UNUSED_LINK_TIME = now

        limit_day = now - datetime.timedelta(seconds=REMOVE_UNUSED_LINK_INTERVAL_SEC)
        query = delete(Link).where(coalesce(Link.last_use_time, Link.creation_time) <= limit_day).returning(Link.code)
        res = await session.execute(query)
        res = res.scalars().all()

        if len(res) > 0:
            coroutine_list = []
            for i in res:
                coroutine_list.append(remove_link(i, redis_client))
            await asyncio.gather(*coroutine_list)
            await session.commit()
