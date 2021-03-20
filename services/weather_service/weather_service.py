import pandas as pd


class WeatherForecastService:

    def get_weather_forecast(self,
                             start_datetime: pd.Timestamp,
                             end_datetime: pd.Timestamp) -> pd.DataFrame:
        raise NotImplementedError
