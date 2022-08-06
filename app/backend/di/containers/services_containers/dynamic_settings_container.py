from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Resource, Object
from dynamic_settings.repository.db_settings_repository import dtype_converters

from backend.constants import default_config
from backend.di.resources.database import dynamic_settings_repository
from backend.services.settings_service import SettingsService


class DynamicSettingsContainer(DeclarativeContainer):
    dynamic_settings_db_session_provider = Dependency()

    settings_repository = Resource(
        dynamic_settings_repository,
        db_session_provider=dynamic_settings_db_session_provider,
        dtype_converters=Object([
            dtype_converters.BooleanDTypeConverter(),
            dtype_converters.DatetimeDTypeConverter(),
            dtype_converters.FloatDTypeConverter(),
            dtype_converters.IntDTypeConverter(),
            dtype_converters.StrDTypeConverter(),
            dtype_converters.NoneDTypeConverter(),
            dtype_converters.TimedeltaDTypeConverter()
        ]),
        default_settings=Object(default_config.DICT)
    )
    settings_service = Singleton(
        SettingsService,
        settings_repository,
        dynamic_settings_db_session_provider
    )
