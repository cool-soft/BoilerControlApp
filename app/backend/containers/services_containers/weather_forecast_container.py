from boiler.data_processing.beetween_filter_algorithm import FullClosedTimestampFilterAlgorithm
from boiler_softm.weather.io.soft_m_async_weather_forecast_online_loader import SoftMAsyncWeatherForecastOnlineLoader
from boiler_softm.weather.io.soft_m_sync_weather_forecast_json_reader import SoftMSyncWeatherForecastJSONReader
from dateutil.tz import gettz
from dependency_injector import containers, providers

from backend.services.weather_forecast_update_service.weather_forecast_service import SimpleWeatherForecastService
from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class WeatherForecastContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_forecast_timezone = providers.Callable(gettz, config.weather_server_timezone)
    weather_forecast_reader = providers.Singleton(
        SoftMSyncWeatherForecastJSONReader,
        weather_data_timezone=weather_forecast_timezone
    )
    weather_forecast_loader = providers.Singleton(
        SoftMAsyncWeatherForecastOnlineLoader,
        reader=weather_forecast_reader
    )

    weather_forecast_repository = providers.Singleton(
        WeatherForecastRepository,
        filter_algorithm=FullClosedTimestampFilterAlgorithm()
    )

    weather_preprocess_algorithm =

    weather_forecast_service = providers.Singleton(
        SimpleWeatherForecastService,
        weather_forecast_loader,
        weather_forecast_repository
    )
