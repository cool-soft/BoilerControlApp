from random import random

import pytest
import pandas as pd
from boiler.constants import dataset_prototypes, column_names
from dateutil.tz import gettz

from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class TestWeatherForecastRepository:
    time_tick = pd.Timedelta(seconds=300)
    forecast_start_timestamp = pd.Timestamp.now(tz=gettz("Asia/Yekaterinburg"))
    forecast_end_timestamp = forecast_start_timestamp + (100 * time_tick)
    forecast_drop_timestamp = forecast_start_timestamp + (10 * time_tick)

    @pytest.fixture
    def repository(self):
        return WeatherForecastRepository()

    @pytest.fixture
    def weather_forecast_df(self):
        forecast_df = dataset_prototypes.WEATHER.copy()

        current_timestamp = self.forecast_start_timestamp
        while current_timestamp < self.forecast_end_timestamp:
            forecast_df = forecast_df.append(
                {
                    column_names.TIMESTAMP: current_timestamp,
                    column_names.WEATHER_TEMP: random()
                },
                ignore_index=True
            )
            current_timestamp += self.time_tick

        return forecast_df

    @pytest.mark.asyncio
    async def test_set_get(self, weather_forecast_df, repository):
        await repository.set_weather_forecast(weather_forecast_df)
        loaded_weather_forecast = await repository.get_weather_forecast_by_timestamp_range(
            self.forecast_start_timestamp,
            self.forecast_end_timestamp
        )
        assert weather_forecast_df.to_dict("records") == loaded_weather_forecast.to_dict("records")

    @pytest.mark.asyncio
    async def test_set_drop_get(self, weather_forecast_df, repository):
        await repository.set_weather_forecast(weather_forecast_df)
        await repository.drop_weather_forecast_older_than(self.forecast_drop_timestamp)
        loaded_weather_forecast = await repository.get_weather_forecast_by_timestamp_range(
            self.forecast_start_timestamp,
            self.forecast_end_timestamp
        )
        assert not loaded_weather_forecast.empty
        assert (weather_forecast_df.columns == loaded_weather_forecast.columns).all()
        assert loaded_weather_forecast[column_names.TIMESTAMP].min() >= self.forecast_drop_timestamp
