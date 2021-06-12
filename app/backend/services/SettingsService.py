from typing import Any, List

from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository

from backend.models.setting.setting_v3 import SettingV3


class SettingsService:

    def __init__(self,
                 settings_repository: AbstractSettingsRepository,
                 ) -> None:
        self._settings_repository = settings_repository

    async def get_setting(self, setting_name: str) -> SettingV3:
        setting_value = await self._settings_repository.get_one(setting_name)
        return SettingV3(name=setting_name, value=setting_value)

    async def set_setting(self, setting_name: str, setting_value: Any) -> None:
        await self._settings_repository.set_one(setting_name, setting_value)

    async def get_all_settings(self) -> List[SettingV3]:
        loaded_settings = await self._settings_repository.get_all()
        response_settings = []
        for loaded_setting_name, loaded_setting_value in loaded_settings.items():
            response_settings.append(
                SettingV3(name=loaded_setting_name, value=loaded_setting_value)
            )
        return response_settings
