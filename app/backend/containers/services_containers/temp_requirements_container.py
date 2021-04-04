from dateutil.tz import gettz
from dependency_injector import containers, providers

from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator
from boiler.weater_info.interpolators.weather_data_linear_interpolator import WeatherDataLinearInterpolator
from boiler.weater_info.parsers.soft_m_json_weather_data_parser import SoftMJSONWeatherDataParser
from boiler.weater_info.repository.online_soft_m_weather_forecast_repository import \
    OnlineSoftMWeatherForecastRepository
from boiler.temp_requirements.repository.temp_requirements_simple_repository import TempRequirementsSimpleRepository
from backend.services.simple_temp_requirements_service import SimpleTempRequirementsService


class TempRequirementsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_repository = providers.Dependency()

    temp_requirements_calculator = providers.Singleton(TempGraphRequirementsCalculator)

    weater_data_timezone = providers.Callable(gettz, config.weather_server_timezone)
    weather_data_parser = providers.Singleton(SoftMJSONWeatherDataParser,
                                              weather_data_timezone=weater_data_timezone)
    weather_data_interpolator = providers.Singleton(WeatherDataLinearInterpolator)
    weather_repository = providers.Singleton(OnlineSoftMWeatherForecastRepository,
                                             weather_data_parser=weather_data_parser,
                                             weather_data_interpolator=weather_data_interpolator)

    temp_requirements_repository = providers.Singleton(TempRequirementsSimpleRepository)

    temp_requirements_service = providers.Singleton(SimpleTempRequirementsService,
                                                    temp_graph_repository=temp_graph_repository,
                                                    weather_repository=weather_repository,
                                                    temp_requirements_repository=temp_requirements_repository,
                                                    temp_graph_requirements_calculator=temp_requirements_calculator)
