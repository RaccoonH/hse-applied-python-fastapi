from fastapi import FastAPI
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from auth.users import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from auth.db import create_db_and_tables
from links.models import create_db_and_tables as create_link_db
from redis import asyncio as aioredis

from links.router import router as links_router
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    app.state.redis_client = aioredis.from_url("redis://localhost:6379")
    await create_db_and_tables()
    await create_link_db()
    yield
    await app.state.redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(links_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
