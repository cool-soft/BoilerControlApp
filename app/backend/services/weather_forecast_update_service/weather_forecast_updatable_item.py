from dependency_injector.providers import Provider
from updater.updatable_item.abstract_sync_updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.services.weather_forecast_update_service.weather_forecast_service import SimpleWeatherForecastService


class WeatherForecastUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self,
                 provider: Provider,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        self._provider = provider

        logger.debug(
            f"Creating instance:"
            f"service provider: {provider}"
        )

    def _run_update(self):
        logger.debug("Run update")
        service: SimpleWeatherForecastService = self._provider()
        service.update_weather_forecast()
