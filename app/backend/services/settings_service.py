from typing import Any, List

from dynamic_settings.repository.abstract_settings_repository import AbstractSyncSettingsRepository
from sqlalchemy.orm import scoped_session

from backend.logging import logger
from backend.models.api import SettingV3


class SettingsService:

    def __init__(self,
                 repository: AbstractSyncSettingsRepository,
                 session_factory: scoped_session
                 ) -> None:
        logger.debug("Creating instance")
        self._settings_repository = repository
        self._session_factory = session_factory

    def get_setting(self, setting_name: str) -> SettingV3:
        logger.info(f"Requesting setting {setting_name}")
        with self._session_factory.begin():
            setting_value = self._settings_repository.get_one(setting_name)
        self._session_factory.remove()
        return SettingV3(name=setting_name, value=setting_value)

    def set_setting(self, setting_name: str, setting_value: Any) -> None:
        logger.info(f"Set setting {setting_name}={setting_value}")
        with self._session_factory.begin() as session:
            self._settings_repository.set_one(setting_name, setting_value)
            session.commit()
        self._session_factory.remove()

    def get_all_settings(self) -> List[SettingV3]:
        logger.info("Requesting all settings")
        with self._session_factory.begin():
            loaded_settings = self._settings_repository.get_all()
        self._session_factory.remove()
        response_settings = []
        for loaded_setting_name, loaded_setting_value in loaded_settings.items():
            response_settings.append(
                SettingV3(name=loaded_setting_name, value=loaded_setting_value)
            )
        return response_settings
