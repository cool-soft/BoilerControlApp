from typing import Optional

import pandas as pd
from boiler.temp_requirements.calculators.abstract_temp_requirements_calculator import \
    AbstractTempRequirementsCalculator
from boiler.weather.io.abstract_sync_weather_loader import AbstractSyncWeatherLoader


class TempRequirementsProvider:

    def __init__(self,
                 weather_forecast_loader: AbstractSyncWeatherLoader,
                 temp_requirements_calculator: AbstractTempRequirementsCalculator,
                 ) -> None:
        self._weather_forecast_loader = weather_forecast_loader
        self._temp_requirements_calculator = temp_requirements_calculator

    def get_temp_requirements(self,
                              start_datetime: Optional[pd.Timestamp] = None,
                              end_datetime: Optional[pd.Timestamp] = None
                              ) -> pd.DataFrame:
        weather_forecast_df = self._weather_forecast_loader.load_weather(start_datetime, end_datetime)
        temp_requirements_df = self._temp_requirements_calculator.calc_for_weather(weather_forecast_df)
        return temp_requirements_df
