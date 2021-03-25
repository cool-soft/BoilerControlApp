from dependency_injector import containers, providers

from services.weather_service.weather_forecast_service_with_cache import WeatherForecastServiceWithCache
from boiler_weater_info.interpolators.weather_data_linear_interpolator import WeatherDataLinearInterpolator
from boiler_weater_info.parsers.soft_m_json_weather_data_parser import SoftMJSONWeatherDataParser
from boiler_weater_info.providers.online_soft_m_weather_forecast_provider import OnlineSoftMWeatherForecastProvider


class OnlinerWeatherForecastContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_data_parser = providers.Singleton(
        SoftMJSONWeatherDataParser,
        weather_data_timezone_name=config.server_timezone
    )

    weather_data_interpolator = providers.Singleton(WeatherDataLinearInterpolator)

    weather_forecast_provider = providers.Singleton(
        OnlineSoftMWeatherForecastProvider,
        weather_data_parser=weather_data_parser,
        weather_data_interpolator=weather_data_interpolator
    )

    weather_forecast_service = providers.Singleton(
        WeatherForecastServiceWithCache,
        update_interval=config.update_interval,
        weather_forecast_provider=weather_forecast_provider
    )
