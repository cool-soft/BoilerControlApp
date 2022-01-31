from boiler.timedelta.io.sync_timedelta_csv_reader import SyncTimedeltaCSVReader
from boiler.timedelta.io.sync_timedelta_file_loader import SyncTimedeltaFileLoader
from boiler_softm.temp_graph.io.soft_m_async_temp_graph_online_loader import SoftMAsyncTempGraphOnlineLoader
from boiler_softm.temp_graph.io.soft_m_sync_temp_graph_json_reader import SoftMSyncTempGraphJSONReader
from boiler_softm.weather.io.soft_m_async_weather_forecast_online_loader \
    import SoftMAsyncWeatherForecastOnlineLoader
from boiler_softm.weather.io.soft_m_sync_weather_forecast_json_reader \
    import SoftMSyncWeatherForecastJSONReader
from dateutil.tz import gettz
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Callable


class Gateways(DeclarativeContainer):
    config = Configuration(strict=True)

    temp_graph_reader = Factory(SoftMSyncTempGraphJSONReader)
    temp_graph_loader = Factory(
        SoftMAsyncTempGraphOnlineLoader,
        reader=temp_graph_reader
    )

    weather_forecast_timezone = Callable(
        gettz,
        config.weather_forecast_loader.weather_server_timezone
    )
    weather_forecast_reader = Factory(
        SoftMSyncWeatherForecastJSONReader,
        weather_data_timezone=weather_forecast_timezone
    )
    weather_forecast_loader = Factory(
        SoftMAsyncWeatherForecastOnlineLoader,
        reader=weather_forecast_reader
    )

    time_delta_loader = Factory(
        SyncTimedeltaFileLoader,
        filepath=config.time_delta_loader.heating_objects_time_delta_path,
        reader=Factory(
            SyncTimedeltaCSVReader,
            separator=";"
        )
    )
