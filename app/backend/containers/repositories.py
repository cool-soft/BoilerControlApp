from boiler.data_processing.beetween_filter_algorithm import FullClosedTimestampFilterAlgorithm
from boiler.temp_graph.io.sync_temp_graph_in_memory_dumper_loader \
    import SyncTempGraphInMemoryDumperLoader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Factory, Resource, Object, Dependency
from dynamic_settings.repository.db_settings_repository import dtype_converters

from backend.constants import default_config
from backend.repositories.control_action_repository import ControlActionsRepository
from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.resources.dynamic_settings_repository_resource import DynamicSettingsRepositoryResource


class Repositories(DeclarativeContainer):
    config = Configuration(strict=True)
    session_factory = Dependency()

    temp_graph_repository = Singleton(SyncTempGraphInMemoryDumperLoader)
    weather_forecast_repository = Singleton(
        WeatherForecastRepository,
        filter_algorithm=Factory(FullClosedTimestampFilterAlgorithm)
    )
    control_actions_repository = Singleton(ControlActionsRepository)
    dynamic_settings_repository = Resource(
        DynamicSettingsRepositoryResource,
        session_factory=session_factory,
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
