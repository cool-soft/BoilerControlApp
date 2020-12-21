from dependency_injector import containers, providers

from services.boiler_t_predictor_service.simple_boiler_t_predictor_service import SimpleBoilerTPredictorService
from services.temp_requirements_service import SimpleTempRequirementsService
from services.weather_service.simple_weather_service import SimpleWeatherService
from resources.home_time_deltas_resource import HomeTimeDeltasResource
from resources.optimized_t_table_resource import OptimizedTTableResource
from resources.temp_graph_resource import TempGraphResource


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    optimized_t_table = providers.Resource(
        OptimizedTTableResource,
        config.boiler_t_prediction_service.optimized_t_table_path
    )

    homes_time_deltas = providers.Resource(
        HomeTimeDeltasResource,
        config.boiler_t_prediction_service.homes_deltas_path
    )

    temp_graph = providers.Resource(
        TempGraphResource,
        config.temp_requirements_service.temp_graph_path
    )

    weather_service = providers.Singleton(
        SimpleWeatherService,
        server_timezone=config.weather_forecast_service.server_timezone,
        server_address=config.weather_forecast_service.server_address,
        update_interval=config.weather_forecast_service.update_interval
    )

    temp_requirements_service = providers.Singleton(
        SimpleTempRequirementsService,
        temp_graph=temp_graph,
        weather_service=weather_service
    )

    boiler_t_predictor_service = providers.Singleton(
        SimpleBoilerTPredictorService,
        optimized_t_table=optimized_t_table,
        home_time_deltas=homes_time_deltas,
        temp_requirements_service=temp_requirements_service,
        home_t_dispersion_coefficient=config.boiler_t_prediction_service.home_t_dispersion_coefficient
    )


class Endpoints(containers.DeclarativeContainer):
    config = providers.Configuration()


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config.services
    )

    endpoints = providers.Container(
        Endpoints,
        config=config.endpoints
    )
