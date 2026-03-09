from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()


class Link(Base):
    __tablename__ = "link"

    code = Column(String, primary_key=True, unique=True, index=True)
    orig_url = Column(String, nullable=False)
    creation_time = Column(DateTime, nullable=False)
    last_use_time = Column(DateTime)
    counter = Column(Integer, default=0, nullable=False)
    creator = Column(String)
    expires_at = Column(DateTime)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
