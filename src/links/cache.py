import datetime
import json
from contextlib import asynccontextmanager

REDIS_GET_TAG = "+"
REDIS_NOT_FOUND_TAG = "-"

REDIS_COUNTER_TAG = 'c'
REDIS_URL_TAG = 'u'
REDIS_USE_TIME_TAG = 't'
REDIS_CREATION_TIME_TAG = 'q'
REDIS_LOCK_TAG = 'l'


async def get_cached_link_url(code: str, redis_client):
    value = await redis_client.get(f'{REDIS_GET_TAG}{code}')
    if value is None:
        return None

    value = json.loads(value)
    value[REDIS_COUNTER_TAG] += 1
    value[REDIS_USE_TIME_TAG] = datetime.datetime.now(datetime.timezone.utc)
    await redis_client.set(f'{REDIS_GET_TAG}{code}', json.dumps(value, default=str))
    return value[REDIS_URL_TAG]


async def get_cached_link_stats(code: str, redis_client):
    value = await redis_client.get(f'{REDIS_GET_TAG}{code}')
    if value is None:
        return None

    value = json.loads(value)
    return {
        "original_url": value[REDIS_URL_TAG],
        "creation_time": value[REDIS_CREATION_TIME_TAG],
        "counter": value[REDIS_COUNTER_TAG],
        "last_use_time": value[REDIS_USE_TIME_TAG]
    }


async def set_link_cache(code: str, url: str, counter, creation_time, redis_client):
    await redis_client.delete(f'{REDIS_NOT_FOUND_TAG}{code}')
    await redis_client.set(f'{REDIS_GET_TAG}{code}', json.dumps({
        REDIS_COUNTER_TAG: counter,
        REDIS_URL_TAG: url,
        REDIS_USE_TIME_TAG: datetime.datetime.now(datetime.timezone.utc),
        REDIS_CREATION_TIME_TAG: creation_time
    }, default=str))


async def update_link_cache(old_code: str, code: str, redis_client):
    value = await redis_client.get(f'{REDIS_GET_TAG}{old_code}')
    if value is None:
        return None

    value = json.loads(value)
    await redis_client.set(f'{REDIS_GET_TAG}{code}', json.dumps(value, default=str))
    await redis_client.delete(f'{REDIS_GET_TAG}{old_code}')
    await redis_client.delete(f'{REDIS_NOT_FOUND_TAG}{code}')
    return value[REDIS_URL_TAG]


async def remove_link(code: str, redis_client):
    await redis_client.delete(f'{REDIS_GET_TAG}{code}')


async def set_not_found_cache(code: str, redis_client, ttl=60):
    await redis_client.set(f'{REDIS_NOT_FOUND_TAG}{code}', 0, ex=ttl)


async def get_not_found_cache(code: str, redis_client):
    res = await redis_client.get(f'{REDIS_NOT_FOUND_TAG}{code}')
    return res is not None


async def remove_not_found_cache(code: str, redis_client):
    await redis_client.delete(f'{REDIS_NOT_FOUND_TAG}{code}')


@asynccontextmanager
async def redis_lock(redis, timeout=10):
    lock = redis.lock(REDIS_LOCK_TAG, timeout=timeout)
    acquired = await lock.acquire()
    try:
        if not acquired:
            raise Exception("Could not acquire lock")
        yield lock
    finally:
        await lock.release()
