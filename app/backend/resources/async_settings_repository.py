import logging

from dependency_injector import resources
from sqlalchemy.orm import scoped_session
from dynamic_settings.repository.db_settings_repository import dtype_converters, DBSettingsRepository
from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncSettingsRepository(resources.AsyncResource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    async def init(self,
                   session_factory: scoped_session) -> SettingsRepository:
        self._logger.debug("Initialize db session factory")

        converters = self._dtype_converters()
        repository = DBSettingsRepository(session_factory=session_factory,
                                          dtype_converters=converters)
        return repository

    # noinspection PyMethodMayBeStatic
    def _dtype_converters(self):
        converters = [
            dtype_converters.BooleanDTypeConverter(),
            dtype_converters.DatetimeDTypeConverter(),
            dtype_converters.FloatDTypeConverter(),
            dtype_converters.IntDTypeConverter(),
            dtype_converters.StrDTypeConverter(),
            dtype_converters.NoneDTypeConverter(),
            dtype_converters.TimedeltaDTypeConverter()
        ]
        return converters

    async def shutdown(self, settings_repository: SettingsRepository) -> None:
        pass
