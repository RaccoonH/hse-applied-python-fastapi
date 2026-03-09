from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import LinkCreate, LinkUpdate
from sqlalchemy import select, insert, exists, delete, update
from auth.db import User
import random
import string
import datetime
from .models import Link
from fastapi import HTTPException

SHORT_CODE_LEN = 8


def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=SHORT_CODE_LEN))


async def db_create_link(info: LinkCreate, session: AsyncSession, user: User):
    while True:
        if info.custom_alias is not None:
            code = info.custom_alias
        else:
            code = generate_code()

        link_exist = await session.scalar(
            select(exists().where(Link.code == code))
        )

        if link_exist:
            if info.custom_alias is not None:
                raise HTTPException(status_code=500, detail={
                    "error": f"There is already link with code: {code}",
                })
            continue

        creator = user.email if user is not None else None
        statement = insert(Link).values(
            orig_url=info.orig_url,
            code=code,
            creation_time=datetime.datetime.now(datetime.timezone.utc),
            expires_at=info.expires_at,
            counter=0,
            creator=creator)
        await session.execute(statement)
        await session.commit()

        return code


async def db_get_link(short_code: str, session: AsyncSession):
    query = select(Link.orig_url, Link.counter, Link.creation_time).where(Link.code == short_code)
    res = await session.execute(query)
    res = res.all()
    if len(res) == 0:
        return None, None, None

    return res[0][0], res[0][1], res[0][2]


async def db_delete_link(short_code: str, session: AsyncSession, user: User):
    query = delete(Link).where(
        (Link.code == short_code) & (Link.creator == user.email)
    )
    res = await session.execute(query)
    await session.commit()
    return res.rowcount != 0


async def db_put_link(old_code: str, info: LinkUpdate, session: AsyncSession, user: User):
    while True:
        if info.custom_alias is not None:
            code = info.custom_alias
        else:
            code = generate_code()

        link_exist = await session.scalar(
            select(exists().where(Link.code == code))
        )

        if link_exist:
            if info.custom_alias is not None:
                raise HTTPException(status_code=500, detail={
                    "error": f"There is already link with code: {code}",
                })
            continue

        update_values = {"code": code}
        if info.expires_at is not None:
            update_values["expires_at"] = info.expires_at

        query = update(Link).where(
            (Link.code == old_code) & (Link.creator == user.email)
        ).values(update_values)
        res = await session.execute(query)
        await session.commit()
        return code if res.rowcount != 0 else None


async def db_get_stats(code: str, session: AsyncSession):
    query = select(Link.orig_url, Link.creation_time, Link.counter, Link.last_use_time).where(Link.code == code)
    res = await session.execute(query)
    res = res.all()
    if len(res) == 0:
        return None
    res = res[0]
    return {
        "original_url": res[0],
        "creation_time": res[1],
        "counter": res[2],
        "last_use_time": res[3],
    }


async def db_update_counter_link(code: str, counter: int, session: AsyncSession):
    query = update(Link).where(Link.code == code).values(counter=counter)
    res = await session.execute(query)
    await session.commit()
    return code if res.rowcount != 0 else None


async def db_search_code(url: str, session: AsyncSession):
    query = select(Link.code).where(Link.orig_url == url)
    res = await session.execute(query)
    return res.scalars().all()
