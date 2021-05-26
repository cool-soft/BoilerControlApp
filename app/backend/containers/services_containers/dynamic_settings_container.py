from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration, Object

from backend.services.SettingsService import SettingsService
from backend.constants import default_config


class DynamicSettingsContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    settings_repository = Dependency()

    settings_service = Singleton(
        SettingsService,
        settings_repository=settings_repository,
        defaults=Object(default_config.DICT)
    )
