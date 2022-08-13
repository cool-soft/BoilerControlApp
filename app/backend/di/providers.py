# TODO: интеграторы di
from typing import Any

from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository
from sqlalchemy.orm import scoped_session


def dynamic_settings_provider(db_session_provider: scoped_session,
                              settings_repository: SyncDBSettingsRepository,
                              setting_name: str
                              ) -> Any:
    with db_session_provider():
        setting_value = settings_repository.get_one(setting_name)
    db_session_provider.remove()
    return setting_value
