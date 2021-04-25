from dateutil.tz import gettz
from dependency_injector import containers, providers

from boiler.temp_requirements.calculators.temp_graph_requirements_calculator \
    import TempGraphRequirementsCalculator
from boiler.temp_requirements.repository.db.async_.temp_requirements_db_async_fake_repository \
    import TempRequirementsDBAsyncFakeRepository
from boiler_softm.weather.io.sync.soft_m_sync_weather_forecast_json_reader \
    import SoftMSyncWeatherForecastJSONReader
from boiler_softm.weather.io.async_.soft_m_async_weather_forecast_online_loader \
    import SoftMAsyncWeatherForecastOnlineLoader
from backend.services.temp_requirements_update_service.simple_temp_requirements_service \
    import SimpleTempRequirementsService


class TempRequirementsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_loader = providers.Dependency()

    temp_requirements_calculator = providers.Singleton(TempGraphRequirementsCalculator)

    weather_forecast_timezone = providers.Callable(gettz, config.weather_server_timezone)
    weather_forecast_reader = providers.Singleton(SoftMSyncWeatherForecastJSONReader,
                                                  weather_data_timezone=weather_forecast_timezone)
    weather_forecast_loader = providers.Singleton(SoftMAsyncWeatherForecastOnlineLoader,
                                                  weather_reader=weather_forecast_reader)

    temp_requirements_repository = providers.Singleton(TempRequirementsDBAsyncFakeRepository)

    temp_requirements_service = providers.Singleton(SimpleTempRequirementsService,
                                                    temp_graph_loader=temp_graph_loader,
                                                    weather_loader=weather_forecast_loader,
                                                    temp_requirements_repository=temp_requirements_repository,
                                                    temp_graph_requirements_calculator=temp_requirements_calculator)
