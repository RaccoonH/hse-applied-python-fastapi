# from .conftest import client
import pytest
from datetime import datetime, timedelta, timezone
from links.watcher import cleanup_expired_links, move_cache_to_database, remove_unused_link, CACHE_TO_DATABASE_INTERVAL_SEC, REMOVE_UNUSED_LINK_INTERVAL_SEC
from .conftest import async_session_maker, fake_redis
from links.database import db_create_link, db_get_link
from links.cache import set_link_cache, get_cached_link_url
from links.schemas import LinkCreate


@pytest.mark.asyncio(loop_scope="session")
async def test_cleanup_expired_links():
    async with async_session_maker() as session:
        date = datetime.now(timezone.utc) + timedelta(hours=1)
        exp_code = "wa_test1"
        exp_url = "http://google.com"

        x = LinkCreate(orig_url=exp_url, expires_at=date, custom_alias=exp_code)
        code, err = await db_create_link(x, session, None)
        assert err is None
        assert code == exp_code

        url, _, _ = await db_get_link(code, session)
        assert url == exp_url

        date_late = date + timedelta(hours=1)
        await cleanup_expired_links(session, fake_redis, date_late)

        url, _, _ = await db_get_link(code, session)
        assert url is None


@pytest.mark.asyncio(loop_scope="session")
async def test_cache_to_database():
    async with async_session_maker() as session:
        exp_code = "wa_test2"
        exp_url = "http://google.com"

        # create link in DB
        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(x, session, None)
        assert err is None
        assert code == exp_code

        # push info in cache
        exp_counter = 10
        date = datetime.now(timezone.utc)
        await set_link_cache(code, exp_url, exp_counter, date, fake_redis)

        # check cache
        result = await get_cached_link_url(code, fake_redis)
        assert result == exp_url

        # check old info in DB
        url, counter, _ = await db_get_link(code, session)
        assert url == exp_url
        assert counter == 0

        # move cache to database
        date_late = date + timedelta(seconds=CACHE_TO_DATABASE_INTERVAL_SEC)
        await move_cache_to_database(session, fake_redis, date_late)

        url, counter, _ = await db_get_link(code, session)
        assert url == exp_url
        # plus one because we did get_cached_link_url
        assert counter == exp_counter + 1

        result = await get_cached_link_url(code, fake_redis)
        assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_remove_unused_link():
    async with async_session_maker() as session:
        exp_code = "wa_test3"
        exp_url = "http://google.com"

        # create link in DB
        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(x, session, None)
        assert err is None
        assert code == exp_code

        url, _, _ = await db_get_link(code, session)
        assert url == exp_url

        # move cache to database
        date_late = datetime.now(timezone.utc) + timedelta(seconds=REMOVE_UNUSED_LINK_INTERVAL_SEC)
        await remove_unused_link(session, fake_redis, date_late, True)

        url, _, _ = await db_get_link(code, session)
        assert url is None
