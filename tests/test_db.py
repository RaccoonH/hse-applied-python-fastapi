# from .conftest import client
import pytest
import pytest
from datetime import datetime, timedelta, timezone
from links.watcher import cleanup_expired_links, move_cache_to_database, remove_unused_link, CACHE_TO_DATABASE_INTERVAL_SEC, REMOVE_UNUSED_LINK_INTERVAL_SEC
from .conftest import async_session_maker, fake_redis
from links.database import db_create_link, db_get_link, db_put_link, db_get_stats, db_update_counter_link, db_search_code, db_delete_link, ERR_ALREADY_LINK
from links.cache import set_link_cache, get_cached_link_url
from links.schemas import LinkCreate, LinkUpdate
from auth.db import User


@pytest.mark.asyncio(loop_scope="session")
async def test_db_create_link():
    async with async_session_maker() as session:
        date = datetime.now(timezone.utc) + timedelta(hours=1)
        exp_code = "db_test1"
        exp_url = "http://google.com"

        x = LinkCreate(orig_url=exp_url, expires_at=date, custom_alias=exp_code)
        code, err = await db_create_link(x, session, None)
        assert err is None
        assert code == exp_code


@pytest.mark.asyncio(loop_scope="session")
async def test_db_create_link_no_custom_code():
    async with async_session_maker() as session:
        exp_url = "http://google.com"

        x = LinkCreate(orig_url=exp_url)
        _, err = await db_create_link(x, session, None)
        assert err is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_create_existed_link():
    async with async_session_maker() as session:
        exp_code = "db_test1"
        exp_url = "http://google.com"

        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        _, err = await db_create_link(x, session, None)
        assert err == ERR_ALREADY_LINK


@pytest.mark.asyncio(loop_scope="session")
async def test_db_get_link():
    async with async_session_maker() as session:
        code = "db_test1"
        exp_url = "http://google.com"
        exp_date = datetime.now()

        url, counter, creation_time = await db_get_link(code, session)
        assert url == exp_url
        assert counter == 0
        assert exp_date - creation_time < timedelta(minutes=1)


@pytest.mark.asyncio(loop_scope="session")
async def test_db_get_non_existed_link():
    async with async_session_maker() as session:
        code = "db_test2"
        url, _, _ = await db_get_link(code, session)
        assert url is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_update_link():
    async with async_session_maker() as session:
        exp_code = "db_updt1"
        exp_url = "http://google.com"
        exp_user = User(email="update@test.com")

        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(x, session, exp_user)
        assert err is None
        assert code == exp_code

        new_code = "db_updt2"
        date = datetime.now(timezone.utc) + timedelta(hours=1)

        upd = LinkUpdate(expires_at=date, custom_alias=new_code)
        url, _ = await db_put_link(exp_code, upd, session, exp_user)
        assert url == new_code


@pytest.mark.asyncio(loop_scope="session")
async def test_db_update_link_wrong_user():
    async with async_session_maker() as session:
        exp_code = "db_wupd1"
        exp_url = "http://google.com"
        exp_user = User(email="update@test.com")
        wrong_user = User(email="wrong@test.com")

        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(x, session, exp_user)
        assert err is None
        assert code == exp_code

        new_code = "db_wupd2"
        date = datetime.now(timezone.utc) + timedelta(hours=1)

        upd = LinkUpdate(expires_at=date, custom_alias=new_code)
        url, _ = await db_put_link(exp_code, upd, session, wrong_user)
        assert url is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_update_existed_new_code():
    async with async_session_maker() as session:
        exp_code = "db_updt1"
        exp_url = "http://google.com"
        exp_user = User(email="update@test.com")

        x = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(x, session, exp_user)
        assert err is None
        assert code == exp_code

        # this code is already taken
        new_code = "db_updt2"
        date = datetime.now(timezone.utc) + timedelta(hours=1)

        upd = LinkUpdate(expires_at=date, custom_alias=new_code)
        url, err = await db_put_link(exp_code, upd, session, exp_user)
        assert url == new_code
        assert err == ERR_ALREADY_LINK


@pytest.mark.asyncio(loop_scope="session")
async def test_db_get_stats():
    async with async_session_maker() as session:
        exp_code = "db_updt2"
        exp_url = "http://google.com"
        exp_date = datetime.now()

        res = await db_get_stats(exp_code, session)
        assert res["original_url"] == exp_url
        assert exp_date - res["creation_time"] < timedelta(minutes=1)
        assert res["counter"] == 0
        assert res["last_use_time"] is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_get_stats_no_existed():
    async with async_session_maker() as session:
        exp_code = "db_noext"
        res = await db_get_stats(exp_code, session)
        assert res is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_update_counter_link():
    async with async_session_maker() as session:
        exp_code = "db_updt2"
        exp_counter = 10
        code = await db_update_counter_link(exp_code, exp_counter, session)
        assert code == exp_code


@pytest.mark.asyncio(loop_scope="session")
async def test_db_update_counter_link_no_existed():
    async with async_session_maker() as session:
        exp_code = "db_noext"
        exp_counter = 10
        code = await db_update_counter_link(exp_code, exp_counter, session)
        assert code is None


@pytest.mark.asyncio(loop_scope="session")
async def test_db_search_code():
    async with async_session_maker() as session:
        exp_codes = ["db_srch1", "db_srch2"]
        exp_url = "http://test.com"
        for code in exp_codes:
            link = LinkCreate(orig_url=exp_url, custom_alias=code)
            code_out, err = await db_create_link(link, session, None)
            assert err is None
            assert code_out == code

        codes = await db_search_code(exp_url, session)
        assert codes == exp_codes


@pytest.mark.asyncio(loop_scope="session")
async def test_db_search_code_wrong_url():
    async with async_session_maker() as session:
        exp_url = "http://no_existed_url.com"
        codes = await db_search_code(exp_url, session)
        assert codes == []


@pytest.mark.asyncio(loop_scope="session")
async def test_db_delete_link():
    async with async_session_maker() as session:
        exp_code = "db_remve"
        exp_user = User(email="remove@test.com")
        exp_url = "http://google.com"


        link = LinkCreate(orig_url=exp_url, custom_alias=exp_code)
        code, err = await db_create_link(link, session, exp_user)
        assert err is None
        assert code == exp_code

        res = await db_delete_link(exp_code, session, exp_user)
        assert res is True
