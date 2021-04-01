from dependency_injector import containers, providers

from backend.services.weather_service.weather_forecast_service_with_cache import AsyncWeatherForecastServiceWithCache
from boiler.weater_info.interpolators.weather_data_linear_interpolator import WeatherDataLinearInterpolator
from boiler.weater_info.parsers.soft_m_json_weather_data_parser import SoftMJSONWeatherDataParser
from boiler.weater_info.repository.online_soft_m_weather_forecast_repository import OnlineSoftMWeatherForecastRepository


class OnlinerWeatherForecastContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_data_parser = providers.Singleton(
        SoftMJSONWeatherDataParser,
        weather_data_timezone_name=config.server_timezone
    )

    weather_data_interpolator = providers.Singleton(WeatherDataLinearInterpolator)

    weather_forecast_provider = providers.Singleton(
        OnlineSoftMWeatherForecastRepository,
        weather_data_parser=weather_data_parser,
        weather_data_interpolator=weather_data_interpolator
    )

    weather_forecast_service = providers.Singleton(
        AsyncWeatherForecastServiceWithCache,
        update_interval=config.update_interval,
        weather_forecast_provider=weather_forecast_provider
    )
