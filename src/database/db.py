from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.conf.config import config


class Base(DeclarativeBase):
    pass

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine = create_async_engine(url, echo=True)
        self._session_maker = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

    async def session(self):
        async with self._session_maker() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
            finally:
                await session.close()

sessionmanager = DatabaseSessionManager(config.sqlalchemy_database_url)
engine = create_async_engine(config.sqlalchemy_database_url)

async def get_db() -> AsyncSession:
    async for session in sessionmanager.session():
        yield session
