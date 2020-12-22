from datetime import datetime

import pandas as pd


class WeatherService:

    def get_weather(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
        raise NotImplementedError
