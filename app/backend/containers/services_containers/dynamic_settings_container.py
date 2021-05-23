from dependency_injector import containers, providers
from dynamic_settings.repository.db_settings_repository import dtype_converters, DBSettingsRepository

from backend.resources.async_settings_db_engine import AsyncSettingsDBEngine
from backend.resources.async_settings_db_session_factory import AsyncSettingsDBSessionFactory
from backend.services.SettingsService import SettingsService


class DynamicSettingsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_engine = providers.Resource(
        AsyncSettingsDBEngine,
        db_url=config.db_url
    )
    session_factory = providers.Resource(
        AsyncSettingsDBSessionFactory,
        db_engine=db_engine
    )
    converters = providers.Object([
        dtype_converters.BooleanDTypeConverter(),
        dtype_converters.DatetimeDTypeConverter(),
        dtype_converters.FloatDTypeConverter(),
        dtype_converters.IntDTypeConverter(),
        dtype_converters.StrDTypeConverter(),
        dtype_converters.NoneDTypeConverter(),
        dtype_converters.TimedeltaDTypeConverter()
    ])
    settings_repository = providers.Singleton(
        DBSettingsRepository,
        session_factory=session_factory,
        dtype_converters=converters
    )

    settings_service = providers.Singleton(
        SettingsService,
        settings_repository=settings_repository,
        defaults=config.defaults
    )
