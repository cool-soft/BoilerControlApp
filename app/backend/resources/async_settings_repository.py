import logging
from copy import copy
from typing import Dict, Any, List

from dependency_injector import resources
from dependency_injector.providers import Configuration
from dynamic_settings.repository.db_settings_repository.dtype_converters import DTypeConverter
from sqlalchemy.orm import scoped_session
from dynamic_settings.repository.db_settings_repository import dtype_converters, DBSettingsRepository
from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncSettingsRepository(resources.AsyncResource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    async def init(self,
                   session_factory: scoped_session,
                   converters: List[DTypeConverter]) -> SettingsRepository:
        self._logger.debug("Initialize db session factory")

        repository = DBSettingsRepository(session_factory=session_factory,
                                          dtype_converters=converters)

        return repository

    async def shutdown(self, settings_repository: SettingsRepository) -> None:
        pass
