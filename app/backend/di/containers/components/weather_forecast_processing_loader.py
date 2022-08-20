from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory

from backend.providers.weather_forecast_provider import WeatherForecastProvider


class WeatherForecastProcessingLoaderContainer(DeclarativeContainer):
    weather_forecast_loader = Dependency()

    weather_forecast_preprocessor = Factory(SoftMLysvaWeatherForecastProcessor)
    weather_forecast_processing_loader = Factory(
        WeatherForecastProvider,
        weather_forecast_loader=weather_forecast_loader,
        weather_forecast_processor=weather_forecast_preprocessor
    )
