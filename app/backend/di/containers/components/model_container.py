from boiler.heating_system.model.corr_table_heating_system_model import CorrTableHeatingSystemModel
from boiler.heating_system.model_requirements.corr_table_model_requirements import \
    CorrTableModelRequirements
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Resource, Configuration, Factory

from backend.di.resources.heating_system_model import \
    heating_system_correlation_table, \
    heating_objects_timedelta


class ModelContainer(DeclarativeContainer):
    config = Configuration(strict=True)

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
    model_requirements = Factory(
        CorrTableModelRequirements,
        timedelta_df
    )
