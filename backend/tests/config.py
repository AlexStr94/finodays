from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.db import Base, get_session
from main import app


SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://test:test@localhost:5432/test'


async def override_get_session() -> AsyncSession:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session