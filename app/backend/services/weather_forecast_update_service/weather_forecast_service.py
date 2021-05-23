from boiler.weather.io.abstract_async_weather_loader import AbstractAsyncWeatherLoader

from backend.repositories.weather_forecast_repository import WeatherForecastRepository


# TODO: Добавить препроцессор
class SimpleWeatherForecastService:

    def __init__(self,
                 weather_forecast_loader: AbstractAsyncWeatherLoader,
                 weather_forecast_repository: WeatherForecastRepository
                 ) -> None:
        self._weather_forecast_loader = weather_forecast_loader
        self._weather_forecast_repository = weather_forecast_repository

    async def update_weather_forecast_async(self) -> None:
        weather_forecast = await self._weather_forecast_loader.load_weather()
        await self._weather_forecast_repository.set_weather(weather_forecast)
