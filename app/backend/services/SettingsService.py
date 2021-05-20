from copy import deepcopy
from typing import Dict, Any

from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository


class SettingsService:

    def __init__(self,
                 settings_repository: AbstractSettingsRepository,
                 defaults: Dict = None
                 ) -> None:
        self._settings_repository = settings_repository
        if defaults is None:
            defaults = {}
        self._defaults = deepcopy(defaults)

    async def initialize(self) -> None:
        current_settings = await self._settings_repository.get_all()
        new_settings = deepcopy(self._defaults)
        new_settings.update(current_settings)
        await self._settings_repository.set_all(new_settings)

    async def get_setting(self, setting_name: str) -> Any:
        return await self._settings_repository.get_one(setting_name)

    async def set_setting(self, setting_name: str, setting_value: Any) -> None:
        await self._settings_repository.set_one(setting_name, setting_value)
