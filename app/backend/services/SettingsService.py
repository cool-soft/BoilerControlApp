from typing import Any

from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository


class SettingsService:

    def __init__(self,
                 settings_repository: AbstractSettingsRepository,
                 ) -> None:
        self._settings_repository = settings_repository

    async def get_setting(self, setting_name: str) -> Any:
        return await self._settings_repository.get_one(setting_name)

    async def set_setting(self, setting_name: str, setting_value: Any) -> None:
        await self._settings_repository.set_one(setting_name, setting_value)
