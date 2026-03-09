from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session, get_redis_client
from urllib.parse import urlparse
from .schemas import LinkCreate, LinkUpdate
from fastapi.responses import RedirectResponse
from auth.users import current_optional_user, current_active_user
from auth.db import User
from .database import db_create_link, db_get_link, db_delete_link, db_put_link, db_get_stats, db_search_code, SHORT_CODE_LEN
from .cache import get_cached_link_url, get_not_found_cache, set_not_found_cache, set_link_cache, remove_link, update_link_cache, get_cached_link_stats
from redis import asyncio as aioredis
from datetime import datetime
from .watcher import watch_event_iterate


router = APIRouter(
    prefix="/links",
    tags=["Link"]
)


def is_valid_url(url):
    try:
        result = urlparse(url)
        if result.scheme and result.netloc:
            return True
        else:
            return False
    except ValueError:
        return False


@router.post("/shorten")
async def create_link(info: LinkCreate, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_optional_user),
                      redis_client: aioredis.Redis = Depends(get_redis_client)):
    if is_valid_url(info.orig_url) is False:
        raise HTTPException(status_code=400, detail={
            "error": "Wrong URL",
        })
    if info.custom_alias is not None and len(info.custom_alias) != SHORT_CODE_LEN:
        raise HTTPException(status_code=400, detail={
            "error": "Short code must be 8 symbols",
        })
    if info.expires_at is not None and info.expires_at <= datetime.now(info.expires_at.tzinfo):
        raise HTTPException(status_code=400, detail={
            "error": "Incorrect expiration date",
        })

    await watch_event_iterate(session, redis_client)

    code = await db_create_link(info, session, user)
    return {
        "status": "success",
        "data": code
    }


@router.get("/search")
async def search_original_url(original_url: str, session: AsyncSession = Depends(get_async_session), redis_client: aioredis.Redis = Depends(get_redis_client)):
    await watch_event_iterate(session, redis_client)

    code = await db_search_code(original_url, session)
    if len(code) == 0:
        raise HTTPException(status_code=404)

    return {
        "status": "success",
        "data": code
    }


@router.get("/{short_code}")
async def get_short_code(short_code: str, session: AsyncSession = Depends(get_async_session), redis_client: aioredis.Redis = Depends(get_redis_client)):
    if len(short_code) != SHORT_CODE_LEN:
        raise HTTPException(status_code=500, detail={
            "error": "Incorrect short code, it must have 8 symbols",
        })

    await watch_event_iterate(session, redis_client)

    not_found = await get_not_found_cache(short_code, redis_client)
    if not_found:
        raise HTTPException(status_code=404)

    url = await get_cached_link_url(short_code, redis_client)
    if url is not None:
        return RedirectResponse(url)

    url, counter, creation_time = await db_get_link(short_code, session)
    if url is None:
        await set_not_found_cache(short_code, redis_client)
        raise HTTPException(status_code=404)

    await set_link_cache(short_code, url, counter + 1, creation_time, redis_client)
    return RedirectResponse(url)


@router.delete("/{short_code}")
async def delete_short_code(short_code: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user), redis_client: aioredis.Redis = Depends(get_redis_client)):
    if len(short_code) != SHORT_CODE_LEN:
        raise HTTPException(status_code=500, detail={
            "error": "Incorrect short code, it must have 8 symbols",
        })

    await watch_event_iterate(session, redis_client)

    not_found = await get_not_found_cache(short_code, redis_client)
    if not_found:
        raise HTTPException(status_code=404)

    res = await db_delete_link(short_code, session, user)
    if res:
        await remove_link(short_code, redis_client)
        return {"status": "success"}
    else:
        await set_not_found_cache(short_code, redis_client)
        raise HTTPException(status_code=404, detail={
            "error": "No found",
        })


@router.put("/{short_code}")
async def put_short_code(info: LinkUpdate, short_code: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),
                         redis_client: aioredis.Redis = Depends(get_redis_client)):
    if len(short_code) != SHORT_CODE_LEN:
        raise HTTPException(status_code=500, detail={
            "error": "Incorrect short code, it must have 8 symbols",
        })
    if info.custom_alias is not None and len(info.custom_alias) != SHORT_CODE_LEN:
        raise HTTPException(status_code=500, detail={
            "error": "Incorrect short code, it must have 8 symbols",
        })

    await watch_event_iterate(session, redis_client)

    not_found = await get_not_found_cache(short_code, redis_client)
    if not_found:
        raise HTTPException(status_code=404)

    new_code = await db_put_link(short_code, info, session, user)
    if new_code is not None:
        await update_link_cache(short_code, new_code, redis_client)
        return {
            "status": "success",
            "data": new_code
        }
    else:
        await set_not_found_cache(short_code, redis_client)
        raise HTTPException(status_code=404, detail={
            "error": "No found",
        })


@router.get("/{short_code}/stats")
async def get_stats(short_code: str, session: AsyncSession = Depends(get_async_session), redis_client: aioredis.Redis = Depends(get_redis_client)):
    await watch_event_iterate(session, redis_client)

    not_found = await get_not_found_cache(short_code, redis_client)
    if not_found:
        raise HTTPException(status_code=404)

    res = await get_cached_link_stats(short_code, redis_client)
    if res is not None:
        return {
            "status": "success",
            "data": res
        }

    res = await db_get_stats(short_code, session)
    if res is not None:
        return {
            "status": "success",
            "data": res
        }
    else:
        raise HTTPException(status_code=404, detail={
            "error": "Not found",
        })
