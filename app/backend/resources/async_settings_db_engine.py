import logging

from dependency_injector import resources
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class AsyncSettingsDBEngine(resources.AsyncResource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    async def init(self, db_url: str) -> AsyncEngine:
        self._logger.debug(f"Initialize db engine with url: {db_url}")

        db_engine = create_async_engine(db_url)
        async with db_engine.begin() as conn:
            await conn.run_sync(Setting.metadata.create_all)

        return db_engine

    async def shutdown(self, db_engine: AsyncEngine) -> None:
        pass
