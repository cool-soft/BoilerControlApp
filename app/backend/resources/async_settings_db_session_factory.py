from dependency_injector import resources
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import scoped_session, sessionmaker
from backend.logger import logger


class AsyncSettingsDBSessionFactory(resources.AsyncResource):

    async def init(self, db_engine: AsyncEngine) -> scoped_session:
        logger.debug("Initialize db session factory")

        session_factory = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=db_engine,
                         class_=AsyncSession),
        )

        return session_factory

    async def shutdown(self, session_factory: scoped_session) -> None:
        pass
