from boiler.control_action.predictors.single_circuit_control_action_predictor import SingleCircuitControlActionPredictor
from boiler.control_action.temp_delta_calculator.single_type_temp_delta_calculator import SingleTypeTempDeltaCalculator
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Callable

from backend.constants import config_names
from backend.di.providers import dynamic_settings_provider


class ControlActionPredictorContainer(DeclarativeContainer):
    db_session_provider = Dependency()
    dynamic_settings_repository = Dependency()
    heating_system_model = Dependency()

    temp_delta_calculator = Factory(SingleTypeTempDeltaCalculator)
    control_action_predictor = Factory(
        SingleCircuitControlActionPredictor,
        temp_delta_calculator=temp_delta_calculator,
        heating_system_model=heating_system_model,
        min_boiler_temp=Callable(
            dynamic_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.MIN_BOILER_TEMP
        ),
        max_boiler_temp=Callable(
            dynamic_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.MAX_BOILER_TEMP
        ),
        min_regulation_step=0.3
    )
