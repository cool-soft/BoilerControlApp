from dependency_injector import containers, providers

from .services_containers.simple_boiler_t_prediction_container import SimpleBoilerTPredictionContainer
from .services_containers.online_soft_m_temp_graph_container import OnlineSoftMTempGraphContainer
from .services_containers.soft_m_weather_forecast_container import SoftMWeatherForecastContainer
from .services_containers.temp_requirements_container import TempRequirementsContainer


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_forecasting = providers.Container(
        SoftMWeatherForecastContainer,
        config=config.weather_forecasting
    )

    temp_graph_providing = providers.Container(
        OnlineSoftMTempGraphContainer,
        config=config.temp_graph_providing
    )

    temp_requirements_calculation = providers.Container(
        TempRequirementsContainer,
        temp_graph_service=temp_graph_providing.temp_graph_service,
        weather_service=weather_forecasting.weather_service
    )

    boiler_t_prediction = providers.Container(
        SimpleBoilerTPredictionContainer,
        config=config.boiler_t_prediction,
        temp_requirements_service=temp_requirements_calculation.temp_requirements_service
    )
