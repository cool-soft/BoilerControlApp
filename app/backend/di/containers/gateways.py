from boiler.timedelta.io.sync_timedelta_csv_reader import SyncTimedeltaCSVReader
from boiler.timedelta.io.sync_timedelta_file_loader import SyncTimedeltaFileLoader
from boiler_softm_lysva.temp_graph.io.softm_lysva_sync_temp_graph_online_loader \
    import SoftMLysvaSyncTempGraphOnlineLoader
from boiler_softm_lysva.temp_graph.io.softm_lysva_sync_temp_graph_online_reader \
    import SoftMLysvaSyncTempGraphOnlineReader
from boiler_softm_lysva.weather.io.softm_lysva_sync_weather_forecast_online_loader \
    import SoftMLysvaSyncWeatherForecastOnlineLoader
from boiler_softm_lysva.weather.io.softm_lysva_sync_weather_forecast_online_reader \
    import SoftMLysvaSyncWeatherForecastOnlineReader
from dateutil.tz import gettz
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Callable, Resource

from backend.di.resources.settings_db_engine import SettingsDBEngine
from backend.di.resources.settings_db_session_factory import SettingsDBSessionFactory


class Gateways(DeclarativeContainer):
    config = Configuration(strict=True)

    session_factory = Resource(
        SettingsDBSessionFactory,
        db_engine=Resource(
            SettingsDBEngine,
            db_url=config.db_settings_url
        )
    )

    temp_graph_reader = Factory(SoftMLysvaSyncTempGraphOnlineReader)
    temp_graph_loader = Factory(
        SoftMLysvaSyncTempGraphOnlineLoader,
        reader=temp_graph_reader
    )

    weather_forecast_timezone = Callable(
        gettz,
        config.weather_forecast_loader.weather_server_timezone
    )
    weather_forecast_reader = Factory(
        SoftMLysvaSyncWeatherForecastOnlineReader,
        weather_data_timezone=weather_forecast_timezone
    )
    weather_forecast_loader = Factory(
        SoftMLysvaSyncWeatherForecastOnlineLoader,
        reader=weather_forecast_reader
    )

    time_delta_loader = Factory(
        SyncTimedeltaFileLoader,
        filepath=config.time_delta_loader.heating_objects_time_delta_path,
        reader=Factory(
            SyncTimedeltaCSVReader,
            separator=","
        )
    )
