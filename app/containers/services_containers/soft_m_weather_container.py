from dependency_injector import containers, providers

from services.weather_service.online_soft_m_weather_service import OnlineSoftMWeatherService
from services.weather_service.weather_data_interpolators.weather_data_linear_interpolator import \
    WeatherDataLinearInterpolator
from services.weather_service.weather_data_parsers.soft_m_weather_parser import SoftMWeatherDataParser


class SoftMWeatherContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_data_parser = providers.Singleton(
        SoftMWeatherDataParser,
        weather_data_timezone_name=config.server_timezone
    )

    weather_data_interpolator = providers.Singleton(WeatherDataLinearInterpolator)

    weather_service = providers.Singleton(
        OnlineSoftMWeatherService,
        server_address=config.server_address,
        update_interval=config.update_interval,
        weather_data_parser=weather_data_parser,
        weather_data_interpolator=weather_data_interpolator
    )
