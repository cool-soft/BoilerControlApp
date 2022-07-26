from copy import deepcopy
from typing import Dict, List

from dependency_injector.resources import Resource
from dynamic_settings.repository.abstract_settings_repository import AbstractSyncSettingsRepository
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository
from dynamic_settings.repository.db_settings_repository.dtype_converters import DTypeConverter
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter

from backend.logging import logger


class DynamicSettingsRepositoryResource(Resource):

    def init(self,
             session_factory,
             dtype_converters: List[DTypeConverter],
             default_settings: Dict
             ) -> AbstractSyncSettingsRepository:
        logger.debug("Initialization of Resource")
        settings_converter = SettingsConverter(dtype_converters)
        settings_repository = SyncDBSettingsRepository(
            session_factory,
            settings_converter
        )
        with session_factory.begin() as session:
            current_settings = settings_repository.get_all()
            new_settings = deepcopy(default_settings)
            new_settings.update(current_settings)
            settings_repository.set_all(new_settings)
            session.commit()

        return settings_repository

    def shutdown(self, settings_repository: SyncDBSettingsRepository) -> None:
        pass
