from copy import deepcopy
from typing import Dict, Any

from dynamic_settings.repository.abstract_settings_repository import AbstractSyncSettingsRepository
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository
from sqlalchemy.orm import scoped_session


def dynamic_settings_repository(db_session_provider: scoped_session,
                                settings_converter: SettingsConverter,
                                default_settings: Dict[str, Any]
                                ) -> AbstractSyncSettingsRepository:
    settings_repository = SyncDBSettingsRepository(db_session_provider, settings_converter)
    with db_session_provider.begin() as session:
        current_settings = settings_repository.get_all()
        new_settings = deepcopy(default_settings)
        new_settings.update(current_settings)
        settings_repository.set_all(new_settings)
        session.commit()
    db_session_provider.remove()
    return settings_repository
