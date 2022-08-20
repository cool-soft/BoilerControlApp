from boiler.control_action.predictors.single_circuit_control_action_predictor import SingleCircuitControlActionPredictor
from boiler.temp_requirements.temp_delta_calculator.single_type_temp_delta_calculator_with_parameters import \
    SingleTypeTempDeltaCalculatorWithParameters
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Callable
from dynamic_settings.repository.di_integration import sync_db_settings_provider

from backend.constants import config_names


class ControlActionPredictorContainer(DeclarativeContainer):
    db_session_provider = Dependency()
    dynamic_settings_repository = Dependency()
    heating_system_model = Dependency()

    temp_delta_calculator = Factory(
        SingleTypeTempDeltaCalculatorWithParameters,
        temp_requirements_coefficient=Callable(
            sync_db_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT
        ),
        min_model_error=Callable(
            sync_db_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.MODEL_ERROR_SIZE
        )
    )
    control_action_predictor = Factory(
        SingleCircuitControlActionPredictor,
        temp_delta_calculator=temp_delta_calculator,
        heating_system_model=heating_system_model,
        min_boiler_temp=Callable(
            sync_db_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.MIN_BOILER_TEMP
        ),
        max_boiler_temp=Callable(
            sync_db_settings_provider,
            db_session_provider,
            dynamic_settings_repository,
            config_names.MAX_BOILER_TEMP
        ),
        min_regulation_step=0.3
    )
