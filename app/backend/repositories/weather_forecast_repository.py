import pandas as pd


class WeatherForecastRepository:

    async def get_weather_forecast_by_timestamp_range(self,
                                                      start_timestamp: pd.Timestamp,
                                                      end_timestamp: pd.Timestamp
                                                      ) -> pd.DataFrame:
        pass

    async def set_weather_forecast(self, weather_df: pd.DataFrame) -> None:
        pass

    async def delete_weather_forecast_older_than(self, timestamp: pd.Timestamp) -> None:
        pass
