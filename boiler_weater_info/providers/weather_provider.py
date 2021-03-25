import pandas as pd


class WeatherProvider:

    def get_weather(self,
                    start_datetime: pd.Timestamp = None,
                    end_datetime: pd.Timestamp = None) -> pd.DataFrame:
        raise NotImplementedError
