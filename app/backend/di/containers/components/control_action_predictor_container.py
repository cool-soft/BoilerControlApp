from boiler.control_action.predictors.single_circuit_control_action_predictor import SingleCircuitControlActionPredictor
from boiler.control_action.temp_delta_calculator.single_type_temp_delta_calculator import SingleTypeTempDeltaCalculator
from boiler.heating_system.model.corr_table_heating_system_model import CorrTableHeatingSystemModel
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Resource, Factory, Callable

from backend.constants import config_names
from backend.di.resources.heating_system_model import heating_system_correlation_table, heating_objects_timedelta
from backend.services.settings_service import SettingsService


def kostyle(settings_service: SettingsService, setting_name: str):
    return settings_service.get_setting(setting_name).value


class ControlActionPredictorContainer(DeclarativeContainer):
    config = Configuration(strict=True)
    dynamic_settings_service = Dependency()

    temp_correlation_table = Resource(
        heating_system_correlation_table,
        filepath=config.temp_correlation_table_path
    )
    timedelta_df = Resource(
        heating_objects_timedelta,
        filepath=config.timedelta_filepath
    )
    heating_system_model = Factory(
        CorrTableHeatingSystemModel,
        temp_correlation_df=temp_correlation_table,
        timedelta_df=timedelta_df,
    )
    control_action_predictor = Factory(
        SingleCircuitControlActionPredictor,
        temp_delta_calculator=Factory(SingleTypeTempDeltaCalculator),
        heating_system_model=heating_system_model,
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
