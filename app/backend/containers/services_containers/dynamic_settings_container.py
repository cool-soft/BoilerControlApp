from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration

from backend.services.SettingsService import SettingsService


class DynamicSettingsContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    session_factory = Dependency()
    settings_repository = Dependency()

    settings_service = Singleton(
        SettingsService,
        settings_repository,
        session_factory
    )
