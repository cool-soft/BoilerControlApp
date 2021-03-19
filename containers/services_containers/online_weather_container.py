from dependency_injector import containers, providers

from heating_system.weather_data.weather_service.online_soft_m_weather_service import OnlineSoftMWeatherService
from heating_system.weather_data.weather_data_interpolators.weather_data_linear_interpolator import \
    WeatherDataLinearInterpolator
from heating_system.weather_data.weather_data_parsers.soft_m_json_weather_data_parser import \
    SoftMJSONWeatherDataParser


class OnlineWeatherContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_data_parser = providers.Singleton(
        SoftMJSONWeatherDataParser,
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
