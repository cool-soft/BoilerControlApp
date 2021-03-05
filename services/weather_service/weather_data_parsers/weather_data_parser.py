import pandas as pd


class WeatherDataParser:

    def parse_weather_data(self, weather_as_text: str) -> pd.DataFrame:
        raise NotImplementedError
