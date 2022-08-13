from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory

from backend.services.settings_service import SettingsService


class DynamicSettingsServiceContainer(DeclarativeContainer):
    db_session_provider = Dependency()
    settings_repository = Dependency()

    settings_service = Factory(
        SettingsService,
        db_session_provider,
        settings_repository
    )
