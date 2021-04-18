import logging

from dependency_injector import resources
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import scoped_session, sessionmaker


class AsyncSettingsDBSessionFactory(resources.AsyncResource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    async def init(self, db_engine: AsyncEngine) -> scoped_session:
        self._logger.debug("Initialize db session factory")

        session_factory = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=db_engine,
                         class_=AsyncSession),
        )

        return session_factory

    async def shutdown(self, session_factory: scoped_session) -> None:
        pass
