from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Object, Resource
from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter
from updater_keychain.keychain_db_repository import KeychainDBRepository

from backend.constants import default_config
from backend.di.resources.dynamic_settings_repository import dynamic_settings_repository
from backend.repositories.control_action_repository import ControlActionRepository
from backend.repositories.temp_graph_repository import TempGraphRepository


class Repositories(DeclarativeContainer):
    db_session_provider = Dependency()

    control_action_cache_repository = Factory(
        ControlActionRepository,
        db_session_provider=db_session_provider
    )
    temp_graph_cache_repository = Factory(
        TempGraphRepository,
        db_session_provider=db_session_provider
    )
    settings_converter = Factory(
        SettingsConverter,
        dtype_converters=Object([
            dtype_converters.BooleanDTypeConverter(),
            dtype_converters.DatetimeDTypeConverter(),
            dtype_converters.FloatDTypeConverter(),
            dtype_converters.IntDTypeConverter(),
            dtype_converters.StrDTypeConverter(),
            dtype_converters.NoneDTypeConverter(),
            dtype_converters.TimedeltaDTypeConverter()
        ])
    )
    dynamic_settings_repository = Resource(
        dynamic_settings_repository,
        db_session_provider=db_session_provider,
        settings_converter=settings_converter,
        default_settings=Object(default_config.DICT)
    )
    keychain_repository = Factory(
        KeychainDBRepository,
        db_session_factory=db_session_provider
    )
