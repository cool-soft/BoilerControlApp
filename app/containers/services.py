from dependency_injector import containers, providers

from resources.home_time_deltas_resource import HomeTimeDeltasResource
from resources.optimized_t_table_resource import OptimizedTTableResource
from services.boiler_t_predictor_service.simple_boiler_t_predictor_service import SimpleBoilerTPredictorService
from services.temp_graph_service.online_temp_graph_service import OnlineTempGraphService
from services.temp_requirements_service.simple_temp_requirements_service import SimpleTempRequirementsService
from services.weather_service.simple_weather_service import SimpleWeatherService


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

    weather_service = providers.Singleton(
        SimpleWeatherService,
        server_timezone=config.weather_forecast_service.server_timezone,
        server_address=config.weather_forecast_service.server_address,
        update_interval=config.weather_forecast_service.update_interval
    )

    temp_graph_service = providers.Singleton(
        OnlineTempGraphService,
        server_address=config.temp_graph_service.server_address,
        update_interval=config.temp_graph_service.update_interval
    )

    temp_requirements_service = providers.Singleton(
        SimpleTempRequirementsService,
        temp_graph_service=temp_graph_service,
        weather_service=weather_service
    )

    boiler_t_predictor_service = providers.Singleton(
        SimpleBoilerTPredictorService,
        optimized_t_table=optimized_t_table,
        home_time_deltas=homes_time_deltas,
        temp_requirements_service=temp_requirements_service,
        home_t_dispersion_coefficient=config.boiler_t_prediction_service.home_t_dispersion_coefficient
    )
