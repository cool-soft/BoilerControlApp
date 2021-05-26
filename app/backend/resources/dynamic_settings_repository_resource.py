from copy import deepcopy
from typing import Dict, List

from dependency_injector.resources import AsyncResource
from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository
from dynamic_settings.repository.db_settings_repository import DBSettingsRepository
from dynamic_settings.repository.db_settings_repository.dtype_converters import DTypeConverter


class DynamicSettingsRepositoryResource(AsyncResource):

    async def init(self,
                   session_factory,
                   dtype_converters: List[DTypeConverter],
                   default_settings: Dict
                   ) -> AbstractSettingsRepository:
        settings_repository = DBSettingsRepository(
            session_factory,
            dtype_converters
        )
        current_settings = await settings_repository.get_all()
        new_settings = deepcopy(default_settings)
        new_settings.update(current_settings)
        await settings_repository.set_all(new_settings)

        return settings_repository

    async def shutdown(self, settings_repository: AbstractSettingsRepository) -> None:
        pass
