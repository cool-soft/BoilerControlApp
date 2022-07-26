import pandas as pd
from boiler.constants import column_names
from boiler.weather.io.abstract_sync_weather_loader import AbstractSyncWeatherLoader
from boiler.weather.processing import AbstractWeatherProcessor
from dateutil.tz import UTC

from backend.logging import logger
from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class SimpleWeatherForecastService:

    def __init__(self,
                 weather_forecast_loader: AbstractSyncWeatherLoader,
                 weather_forecast_processor: AbstractWeatherProcessor,
                 weather_forecast_repository: WeatherForecastRepository,
                 preload_timedelta: pd.Timedelta = pd.Timedelta(hours=3),
                 ) -> None:
        logger.debug("Creating instance")
        self._weather_forecast_loader = weather_forecast_loader
        self._weather_forecast_processor = weather_forecast_processor
        self._weather_forecast_repository = weather_forecast_repository
        self._preload_timedelta = preload_timedelta

    def update_weather_forecast(self) -> None:
        logger.info("Requesting weather forecast update")

        weather_forecast_df = self._weather_forecast_loader.load_weather()
        weather_forecast_df = self._process_weather_forecast(
            weather_forecast_df
        )
        self._weather_forecast_repository.set_weather_forecast(weather_forecast_df)

    def _process_weather_forecast(self, weather_forecast_df: pd.DataFrame) -> pd.DataFrame:
        start_timestamp = pd.Timestamp.now(tz=UTC)
        end_timestamp = start_timestamp + self._preload_timedelta
        weather_forecast_df = weather_forecast_df.copy()
        weather_forecast_df[column_names.TIMESTAMP] = weather_forecast_df[column_names.TIMESTAMP].dt.tz_convert(UTC)
        self._weather_forecast_processor.process_weather_df(
            weather_forecast_df,
            start_timestamp,
            end_timestamp
        )
        return weather_forecast_df
