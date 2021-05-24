from boiler.data_processing.beetween_filter_algorithm import FullClosedTimestampFilterAlgorithm
from boiler.temp_graph.io.sync_temp_graph_in_memory_dumper_loader \
    import SyncTempGraphInMemoryDumperLoader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Factory, Resource, Object
from dynamic_settings.repository.db_settings_repository import dtype_converters, DBSettingsRepository

from backend.repositories.control_action_repository import ControlActionsRepository
from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.resources.async_settings_db_engine import AsyncSettingsDBEngine
from backend.resources.async_settings_db_session_factory import AsyncSettingsDBSessionFactory


class Repositories(DeclarativeContainer):
    config = Configuration()

    temp_graph_repository = Singleton(SyncTempGraphInMemoryDumperLoader)
    weather_forecast_repository = Singleton(
        WeatherForecastRepository,
        filter_algorithm=Factory(FullClosedTimestampFilterAlgorithm)
    )
    control_actions_repository = Singleton(ControlActionsRepository)
    settings_repository = Singleton(
        DBSettingsRepository,
        session_factory=Resource(
            AsyncSettingsDBSessionFactory,
            db_engine=Resource(
                AsyncSettingsDBEngine,
                db_url=config.settings_db_url
            )
        ),
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
