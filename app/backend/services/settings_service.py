from typing import Any, List

from dynamic_settings.repository.abstract_settings_repository import AbstractSyncSettingsRepository
from sqlalchemy.orm import scoped_session

from backend.logging import logger
from backend.models.api import SettingAPIModel


class SettingsService:

    def __init__(self, db_session_provider: scoped_session, repository: AbstractSyncSettingsRepository) -> None:
        logger.debug("Creating instance")
        self.db_session_provider = db_session_provider
        self._settings_repository = repository

    def get_setting(self, setting_name: str) -> SettingAPIModel:
        logger.info(f"Requested setting {setting_name}")
        with self.db_session_provider.begin():
            setting_value = self._settings_repository.get_one(setting_name)
        self.db_session_provider.remove()
        return SettingAPIModel(name=setting_name, value=setting_value)

    def set_setting(self, setting_name: str, setting_value: Any) -> None:
        logger.info(f"Set setting {setting_name}={setting_value}")
        with self.db_session_provider.begin() as session:
            self._settings_repository.set_one(setting_name, setting_value)
            session.commit()
        self.db_session_provider.remove()

    def get_all_settings(self) -> List[SettingAPIModel]:
        logger.info("Requesting all settings")
        with self.db_session_provider.begin():
            loaded_settings = self._settings_repository.get_all()
        self.db_session_provider.remove()
        response_settings = []
        for loaded_setting_name, loaded_setting_value in loaded_settings.items():
            response_settings.append(SettingAPIModel(name=loaded_setting_name, value=loaded_setting_value))
        return response_settings
