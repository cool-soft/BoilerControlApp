from dependency_injector import containers, providers

from boiler_temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from resources.home_time_deltas_resource import HomeTimeDeltasResource
from resources.optimized_t_table_resource import TempCorrelationTable
from services.boiler_temp_prediction_service.corr_table_boiler_temp_prediction_service import \
    CorrTableBoilerTempPredictionService


class CorrTableBoilerTempPredictionContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_requirements_service = providers.Dependency()

    temp_correlation_table = providers.Resource(
        TempCorrelationTable,
        config.temp_correlation_table_path
    )

    homes_time_deltas = providers.Resource(
        HomeTimeDeltasResource,
        config.homes_deltas_path
    )

    corr_table_temp_predictor = providers.Singleton(
        CorrTableTempPredictor,
        temp_correlation_table=temp_correlation_table,
        home_time_deltas=homes_time_deltas,
        home_min_temp_coefficient=config.home_min_temp_coefficient
    )

    boiler_temp_prediction_service = providers.Singleton(
        CorrTableBoilerTempPredictionService,
        temp_predictor=corr_table_temp_predictor,
        temp_requirements_service=temp_requirements_service
    )