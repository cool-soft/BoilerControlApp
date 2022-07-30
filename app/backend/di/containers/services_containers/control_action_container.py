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
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Resource, Factory, Callable

from backend.constants import config_names
from backend.di.resources.heating_obj_timedelta_resource import HeatingObjTimedeltaResource
from backend.di.resources.temp_correlation_table import TempCorrelationTable
from backend.services.settings_service import SettingsService
from backend.services.control_action_prediction_service import \
    ControlActionPredictionService


def kostyle(settings_service: SettingsService, setting_name: str):
    return settings_service.get_setting(setting_name).value


class ControlActionContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    temp_graph_repository = Dependency()
    weather_forecast_repository = Dependency()
    control_actions_repository = Dependency()
    dynamic_settings_service = Dependency()
    time_delta_loader = Dependency()

    # TODO: перевести на репозиторий
    temp_correlation_table = Resource(
        TempCorrelationTable,
        config.temp_correlation_table_path
    )

    # TODO: перевести на репозиторий
    time_delta_df = Resource(
        HeatingObjTimedeltaResource,
        loader=time_delta_loader
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
        temp_requirements_coefficient=Callable(
            kostyle,
            dynamic_settings_service,
            config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT
        ),
        min_model_error=Callable(
            kostyle,
            dynamic_settings_service,
            config_names.MODEL_ERROR_SIZE
        ),
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
        min_boiler_temp=Callable(
            kostyle,
            dynamic_settings_service,
            config_names.MIN_BOILER_TEMP
        ),
        max_boiler_temp=Callable(
            kostyle,
            dynamic_settings_service,
            config_names.MAX_BOILER_TEMP
        ),
        min_regulation_step=0.3
    )

    temp_prediction_service = Factory(
        ControlActionPredictionService,
        weather_forecast_repository=weather_forecast_repository,
        control_actions_repository=control_actions_repository,
        control_action_predictor=control_action_predictor,
        model_requirements=model_requirements,
        timestamp_round_algo=timestamp_round_algo,
        timedelta=TIME_TICK,
        timedelta_predict_forward=pd.Timedelta(seconds=3600)
    )
