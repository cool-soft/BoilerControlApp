from dependency_injector import containers, providers

from boiler.temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from backend.repositories.control_action_simple_repository import ControlActionsSimpleRepository
from backend.resources.home_time_deltas_resource import HomeTimeDeltasResource
from backend.resources.temp_correlation_table import TempCorrelationTable
from backend.services.control_action_prediction_service.corr_table_control_action_prediction_service import \
    CorrTableControlActionPredictionService


class ControlActionContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_requirements_repository = providers.Dependency()
    control_actions_repository = providers.Singleton(ControlActionsSimpleRepository)

    temp_correlation_table = providers.Resource(
        TempCorrelationTable,
        config.temp_correlation_table_path
    )

    homes_time_deltas = providers.Resource(
        HomeTimeDeltasResource,
        config.homes_deltas_path
    )

    temp_predictor = providers.Singleton(
        CorrTableTempPredictor,
        temp_correlation_table=temp_correlation_table,
        home_time_deltas=homes_time_deltas,
        home_min_temp_coefficient=config.home_min_temp_coefficient
    )

    temp_prediction_service = providers.Singleton(
        CorrTableControlActionPredictionService,
        temp_predictor=temp_predictor,
        temp_requirements_repository=temp_requirements_repository,
        control_actions_repository=control_actions_repository
    )
