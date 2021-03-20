from dependency_injector import containers, providers

from .services_containers.corr_table_boiler_temp_prediction_container import CorrTableBoilerTempPredictionContainer
from .services_containers.online_temp_graph_container import OnlineTempGraphContainer
from .services_containers.online_weather_forecast_container import OnlinerWeatherForecastContainer
from .services_containers.simple_temp_requirements_container import SimpleTempRequirementsContainer


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_information_providing = providers.Container(
        OnlinerWeatherForecastContainer,
        config=config.weather_information_providing
    )

    temp_graph_providing = providers.Container(
        OnlineTempGraphContainer,
        config=config.temp_graph_providing
    )

    temp_requirements_calculation = providers.Container(
        SimpleTempRequirementsContainer,
        temp_graph_service=temp_graph_providing.temp_graph_service,
        weather_service=weather_information_providing.weather_forecast_service
    )

    boiler_temp_prediction = providers.Container(
        CorrTableBoilerTempPredictionContainer,
        config=config.boiler_temp_prediction,
        temp_requirements_service=temp_requirements_calculation.temp_requirements_service
    )
