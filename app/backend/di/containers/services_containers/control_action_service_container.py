from datetime import timedelta

from boiler.constants.time_tick import TIME_TICK
from boiler.data_processing.timestamp_round_algorithm import CeilTimestampRoundAlgorithm
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Configuration, Callable, Object

from backend.services.control_action_prediction_service import ControlActionPredictionService
from backend.services.control_action_report_service import ControlActionReportService


class ControlActionServiceContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    db_session_provider = Dependency()
    temp_requirements_provider = Dependency()
    control_action_repository = Dependency()
    model_parameters = Dependency()
    control_action_predictor = Dependency()

    timestamp_round_algo = Factory(
        CeilTimestampRoundAlgorithm,
        round_step=Object(TIME_TICK)
    )
    control_action_prediction_service = Factory(
        ControlActionPredictionService,
        model_parameters=model_parameters,
        temp_requirements_provider=temp_requirements_provider,
        control_action_predictor=control_action_predictor,
        db_session_factory=db_session_provider,
        control_action_repository=control_action_repository,
        timestamp_round_algo=timestamp_round_algo,
        time_tick=Object(TIME_TICK),
        timedelta_predict_forward=Callable(timedelta, seconds=config.timedelta_predict_forward)
    )
    control_action_report_service = Factory(
        ControlActionReportService,
        db_session_provider=db_session_provider,
        control_action_repository=control_action_repository
    )
