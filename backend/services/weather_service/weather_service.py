import pandas as pd


class WeatherService:

    def get_weather(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp) -> pd.DataFrame:
        raise NotImplementedError
