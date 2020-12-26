from dependency_injector import containers, providers

from resources.home_time_deltas_resource import HomeTimeDeltasResource
from resources.optimized_t_table_resource import OptimizedTTableResource
from services.boiler_t_predictor_service.simple_boiler_t_predictor_service import SimpleBoilerTPredictorService


class SimpleBoilerTPredictionContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_requirements_service = providers.Dependency()

    optimized_t_table = providers.Resource(
        OptimizedTTableResource,
        config.optimized_t_table_path
    )

    homes_time_deltas = providers.Resource(
        HomeTimeDeltasResource,
        config.homes_deltas_path
    )

    boiler_t_predictor_service = providers.Singleton(
        SimpleBoilerTPredictorService,
        optimized_t_table=optimized_t_table,
        home_time_deltas=homes_time_deltas,
        temp_requirements_service=temp_requirements_service,
        home_t_dispersion_coefficient=config.home_t_dispersion_coefficient
    )
