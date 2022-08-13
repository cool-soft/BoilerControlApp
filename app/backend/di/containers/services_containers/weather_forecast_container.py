import pandas as pd
from boiler_softm_lysva.weather.io import SoftMLysvaSyncWeatherForecastOnlineReader, \
    SoftMLysvaSyncWeatherForecastOnlineLoader
from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Object, Dependency, Singleton

from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.providers.weather_forecast_provider import WeatherForecastService


class WeatherForecastContainer(DeclarativeContainer):
    db_session_provider = Dependency()

    weather_forecast_repository = Singleton(
        WeatherForecastRepository,
        db_session_provider=db_session_provider
    )
    weather_forecast_reader = Factory(SoftMLysvaSyncWeatherForecastOnlineReader)
    weather_forecast_loader = Factory(
        SoftMLysvaSyncWeatherForecastOnlineLoader,
        reader=weather_forecast_reader
    )
    weather_forecast_preprocessor = Factory(SoftMLysvaWeatherForecastProcessor)
    weather_forecast_update_service = Factory(
        WeatherForecastService,
        session_provider=db_session_provider,
        weather_forecast_loader=weather_forecast_loader,
        weather_forecast_processor=weather_forecast_preprocessor,
        weather_forecast_repository=weather_forecast_repository,
        preload_timedelta=Object(pd.Timedelta(hours=3))  # Как рассчитывать?
    )
