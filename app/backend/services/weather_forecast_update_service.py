from typing import Callable

import pandas as pd
from boiler.weather.io.abstract_sync_weather_loader import AbstractSyncWeatherLoader
from boiler.weather.processing import AbstractWeatherProcessor
from dateutil.tz import UTC
from sqlalchemy.orm import Session

from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class WeatherForecastUpdateService:

    def __init__(self,
                 weather_forecast_loader: AbstractSyncWeatherLoader,
                 weather_forecast_processor: AbstractWeatherProcessor,
                 weather_forecast_repository: WeatherForecastRepository,
                 session_provider: Callable[..., Session],
                 preload_timedelta: pd.Timedelta = pd.Timedelta(hours=3)
                 ) -> None:
        self._session_provider = session_provider
        self._weather_forecast_loader = weather_forecast_loader
        self._weather_forecast_processor = weather_forecast_processor
        self._weather_forecast_repository = weather_forecast_repository
        self._preload_timedelta = preload_timedelta

    def update_weather_forecast(self) -> None:
        start_timestamp = pd.Timestamp.now(tz=UTC)
        end_timestamp = start_timestamp + self._preload_timedelta
        weather_forecast_df = self._weather_forecast_loader.load_weather(start_timestamp, end_timestamp)
        weather_forecast_df = self._weather_forecast_processor.process_weather_df(
            weather_forecast_df,
            start_timestamp,
            end_timestamp
        )
        with self._session_provider().begin() as session:
            self._weather_forecast_repository.add_weather_forecast(weather_forecast_df)
            session.commit()
