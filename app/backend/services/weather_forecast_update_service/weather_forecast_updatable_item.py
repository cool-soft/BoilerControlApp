from dependency_injector.providers import Provider
from updater.updatable_item.simple_updatable_item import SimpleUpdatableItem

from backend.services.weather_forecast_update_service.weather_forecast_service import SimpleWeatherForecastService


class WeatherForecastUpdatableItem(SimpleUpdatableItem):

    def __init__(self,
                 provider: Provider,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        self._provider = provider

        self._logger.debug(f"Service provider is set to {provider}")

    async def _run_update_async(self):
        self._logger.debug("Run update")
        service: SimpleWeatherForecastService = self._provider()
        await service.update_weather_forecast_async()