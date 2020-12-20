from datetime import datetime

import pandas as pd


class WeatherForecastService:

    def get_weather_forecast(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
        raise NotImplementedError
