from typing import Optional

import pandas as pd
from boiler.weather.io.abstract_sync_weather_loader import AbstractSyncWeatherLoader
from boiler.weather.processing import AbstractWeatherProcessor


class WeatherForecastProvider(AbstractSyncWeatherLoader):

    def __init__(self,
                 weather_forecast_loader: AbstractSyncWeatherLoader,
                 weather_forecast_processor: AbstractWeatherProcessor
                 ) -> None:
        self._weather_forecast_loader = weather_forecast_loader
        self._weather_forecast_processor = weather_forecast_processor

    def load_weather(self,
                     start_datetime: Optional[pd.Timestamp] = None,
                     end_datetime: Optional[pd.Timestamp] = None
                     ) -> pd.DataFrame:
        weather_forecast_df = self._weather_forecast_loader.load_weather(start_datetime, end_datetime)
        weather_forecast_df = self._weather_forecast_processor.process_weather_df(
            weather_forecast_df,
            start_datetime,
            end_datetime
        )
        return weather_forecast_df
