import pandas as pd
from boiler.constants.time_tick import TIME_TICK
from boiler.control_action.predictors.single_circuit_control_action_predictor \
    import SingleCircuitControlActionPredictor
from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from boiler.data_processing.timestamp_round_algorithm import CeilTimestampRoundAlgorithm
from boiler.heating_system.model.corr_table_heating_system_model import CorrTableHeatingSystemModel
from boiler.heating_system.model_requirements.timedelta_model_requirements_without_history \
    import TimedeltaModelRequirementsWithoutHistory
from boiler.temp_requirements.constraint.single_type_heating_obj_on_weather_constraint \
    import SingleTypeHeatingObjOnWeatherConstraint
from boiler.temp_requirements.predictors.temp_graph_requirements_predictor \
    import TempGraphRequirementsPredictor
from boiler.timedelta.io.sync_timedelta_csv_reader import SyncTimedeltaCSVReader
from boiler.timedelta.io.sync_timedelta_file_loader import SyncTimedeltaFileLoader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Resource, Factory

from backend.resources.heating_obj_timedelta_resource import HeatingObjTimedeltaResource
from backend.resources.temp_correlation_table import TempCorrelationTable
from backend.services.control_action_prediction_service.control_action_prediction_service import \
    ControlActionPredictionService


class ControlActionContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    temp_graph_repository = Dependency()
    weather_forecast_repository = Dependency()
    control_actions_repository = Dependency()

    # TODO: перевести на репозиторий
    temp_correlation_table = Resource(
        TempCorrelationTable,
        config.temp_correlation_table_path
    )

    # TODO: перевести на репозиторий
    time_delta_df = Resource(
        HeatingObjTimedeltaResource,
        loader=Factory(
            SyncTimedeltaFileLoader,
            config.heating_objects_timedeldelta_path,
            Factory(SyncTimedeltaCSVReader)
        )
    )

    model_requirements = Factory(
        TimedeltaModelRequirementsWithoutHistory,
        time_delta_df
    )

    timestamp_round_algo = Factory(
        CeilTimestampRoundAlgorithm,
        round_step=TIME_TICK
    )

    temp_constrains = Factory(
        SingleTypeHeatingObjOnWeatherConstraint,
        temp_requirements_predictor=Factory(
            TempGraphRequirementsPredictor,
            temp_graph=temp_graph_repository.provided.load_temp_graph.call(),
            weather_temp_round_algorithm=Factory(ArithmeticFloatRoundAlgorithm)
        ),
        timestamp_round_algo=timestamp_round_algo,
        temp_requirements_coefficient=0.97,
        min_model_error=1.0
    )

    heating_system_model = Factory(
        CorrTableHeatingSystemModel,
        temp_correlation_df=temp_correlation_table,
        timedelta_df=time_delta_df,
    )

    control_action_predictor = Factory(
        SingleCircuitControlActionPredictor,
        heating_system_model=heating_system_model,
        temp_requirements_constraint=temp_constrains,
        min_boiler_temp=30,
        max_boiler_temp=85,
        min_regulation_step=0.1
    )

    temp_prediction_service = Factory(
        ControlActionPredictionService,
        weather_forecast_repository=weather_forecast_repository,
        control_actions_repository=control_actions_repository,
        control_action_predictor=control_action_predictor,
        model_requirements=model_requirements,
        timestamp_round_algo=timestamp_round_algo,
        timedelta=TIME_TICK,
        timedelta_predict_forward=pd.Timedelta(seconds=3600),
        executor=None
    )
