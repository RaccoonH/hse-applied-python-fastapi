import pytest
from fastapi.testclient import TestClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi import Request
import asyncio
from httpx import AsyncClient, ASGITransport
import fakeredis
from sqlalchemy.pool import NullPool
from redis import asyncio as aioredis
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uuid

from dotenv import load_dotenv
import os

from main import app
from database import get_async_session, get_redis_client
import auth.db as auth
from auth.users import current_active_user, current_optional_user
import links.models as links

load_dotenv()
DB_FILE_TEST = os.getenv("DB_FILE_TEST")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE_TEST}"

engine_test = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
user_id = uuid.uuid4()
fake_redis = fakeredis.aioredis.FakeRedis()


@asynccontextmanager
async def mock_lifespan(_: FastAPI):
    yield


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_redis_client_test(request: Request) -> aioredis.Redis:
    return fake_redis


async def get_redis_client_test_new_everytime(request: Request) -> aioredis.Redis:
    return fakeredis.aioredis.FakeRedis()


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(auth.Base.metadata.create_all)
        await conn.run_sync(links.Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(auth.Base.metadata.drop_all)
        await conn.run_sync(links.Base.metadata.drop_all)


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_client] = get_redis_client_test
    app.router.lifespan_context = mock_lifespan
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_client] = get_redis_client_test_new_everytime
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def ac_logined() -> AsyncGenerator[AsyncClient, None]:
    mock_user = auth.User(
        id=user_id,
        email="example@test.com",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    async def get_current_user_test():
        return mock_user

    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_client] = get_redis_client_test_new_everytime
    app.dependency_overrides[current_active_user] = get_current_user_test
    app.dependency_overrides[current_optional_user] = get_current_user_test
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def ac_logined_redis() -> AsyncGenerator[AsyncClient, None]:
    mock_user = auth.User(
        id=user_id,
        email="example@test.com",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    async def get_current_user_test():
        return mock_user

    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_client] = get_redis_client_test
    app.dependency_overrides[current_active_user] = get_current_user_test
    app.dependency_overrides[current_optional_user] = get_current_user_test
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
