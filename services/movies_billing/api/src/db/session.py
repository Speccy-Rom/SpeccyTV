from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

engine = create_async_engine(settings.postgres_dsn)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


async def get_db() -> Session:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
                if not settings.test:
                    await session.commit()
            finally:
                await session.close()
