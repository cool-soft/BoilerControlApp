import pandas as pd
from boiler.constants import circuit_types
from boiler.constants.time_tick import TIME_TICK
from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from boiler.data_processing.timestamp_round_algorithm import CeilTimestampRoundAlgorithm
from boiler.heating_system.model_requirements.corr_table_model_requirements import CorrTableModelRequirements
from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Callable, Singleton, Container, Configuration
from sqlalchemy.orm import scoped_session

from backend.di.containers.components.control_action_predictor_container import ControlActionPredictorContainer
from backend.repositories.control_action_repository import ControlActionRepository
from backend.repositories.temp_graph_repository import TempGraphRepository
from backend.services.control_action_prediction_service import ControlActionPredictionService
from backend.services.control_action_report_service import ControlActionReportService


def kostyle2(temp_graph_repository: TempGraphRepository, session_factory: scoped_session):
    with session_factory.begin():
        temp_graph_df = temp_graph_repository.get_temp_graph_for_circuit_type(circuit_types.HEATING)
    session_factory.remove()
    return temp_graph_df


class ControlActionContainer(DeclarativeContainer):
    config = Configuration(strict=True)
    db_session_provider = Dependency()
    dynamic_settings_service = Dependency()
    control_action_predictor_pkg = Container(
        ControlActionPredictorContainer,
        config=config.prediction,
        dynamic_settings_service=dynamic_settings_service
    )
    temp_graph_repository = Dependency()
    weather_forecast_repository = Dependency()

    control_action_repository = Singleton(
        ControlActionRepository,
        db_session_provider=db_session_provider
    )
    model_requirements = Factory(
        CorrTableModelRequirements,
        control_action_predictor_pkg.timedelta_df
    )
    timestamp_round_algo = Factory(
        CeilTimestampRoundAlgorithm,
        round_step=TIME_TICK
    )
    temp_requirements_calculator = Factory(
        TempGraphRequirementsCalculator,
        temp_graph=Callable(
            kostyle2,
            temp_graph_repository,
            db_session_provider
        ),
        weather_temp_round_algorithm=Factory(ArithmeticFloatRoundAlgorithm)
    )
    control_action_prediction_service = Factory(
        ControlActionPredictionService,
        db_session_factory=db_session_provider,
        weather_forecast_repository=weather_forecast_repository,
        control_action_repository=control_action_repository,
        control_action_predictor=control_action_predictor_pkg.control_action_predictor,
        model_requirements=model_requirements,
        timestamp_round_algo=timestamp_round_algo,
        time_tick=TIME_TICK,
        timedelta_predict_forward=pd.Timedelta(seconds=3600),
        temp_requirements_calculator=temp_requirements_calculator
    )
    control_action_report_service = Factory(
        ControlActionReportService,
        db_session_factory=db_session_provider,
        control_action_repository=control_action_repository
    )
