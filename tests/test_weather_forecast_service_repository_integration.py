from random import random
from typing import Optional, Union

import pandas as pd
import pytest
from boiler.constants import column_names
from boiler.weather.io.abstract_sync_weather_loader import AbstractSyncWeatherLoader
from boiler.weather.processing import AbstractWeatherProcessor
from dateutil.tz import gettz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import WeatherForecast
from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.services.weather_forecast_service import WeatherForecastService


class TestWeatherForecastServiceRepositoryIntegration:
    time_tick = pd.Timedelta(seconds=300)
    timezone = gettz("Asia/Yekaterinburg")
    db_url = "sqlite:///:memory:"

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            WeatherForecast.metadata.drop_all(conn)
            WeatherForecast.metadata.create_all(conn)
        db_session_maker = sessionmaker(
            autocommit=False,
            bind=engine
        )
        session_factory = scoped_session(
            db_session_maker
        )
        return session_factory

    @pytest.fixture
    def weather_forecast_repository(self, session_factory):
        return WeatherForecastRepository(session_factory)

    @pytest.fixture
    def weather_forecast_loader(self):
        class WeatherForecastMockLoader(AbstractSyncWeatherLoader):

            def __init__(self, timezone, time_tick):
                self._weather_forecast = None
                self._timezone = timezone
                self._time_tick = time_tick

            def load_weather(self,
                             start_datetime: Optional[pd.Timestamp] = None,
                             end_datetime: Optional[pd.Timestamp] = None
                             ) -> pd.DataFrame:
                if self._weather_forecast is None:
                    self._weather_forecast = self._generate_weather_forecast(start_datetime, end_datetime)
                return self._weather_forecast.copy()

            def _generate_weather_forecast(self, start_datetime, end_datetime) -> pd.DataFrame:
                forecast_list = []
                current_timestamp = start_datetime
                while current_timestamp < end_datetime:
                    forecast_list.append(
                        {
                            column_names.TIMESTAMP: current_timestamp,
                            column_names.WEATHER_TEMP: random()
                        }
                    )
                    current_timestamp += self._time_tick
                forecast_df = pd.DataFrame(forecast_list)
                return forecast_df

        return WeatherForecastMockLoader(self.timezone, self.time_tick)

    @pytest.fixture
    def weather_forecast_processor(self):
        class MockWeatherProcessor(AbstractWeatherProcessor):
            def process_weather_df(self,
                                   weather_df: pd.DataFrame,
                                   min_required_timestamp: Union[pd.Timestamp, None],
                                   max_required_timestamp: Union[pd.Timestamp, None]
                                   ) -> pd.DataFrame:
                return weather_df.copy()

        return MockWeatherProcessor()

    @pytest.fixture
    def weather_forecast_update_service(self,
                                        session_factory,
                                        weather_forecast_repository,
                                        weather_forecast_loader,
                                        weather_forecast_processor):
        return WeatherForecastService(
            weather_forecast_loader,
            weather_forecast_processor,
            weather_forecast_repository,
            session_factory,
        )

    def test_weather_forecast_update_and_drop_older(self,
                                                    weather_forecast_update_service,
                                                    weather_forecast_loader,
                                                    weather_forecast_repository,
                                                    session_factory):
        weather_forecast_update_service.update_weather_forecast()
        original_weather_forecast = weather_forecast_loader.load_weather()
        with session_factory.begin():
            loaded_weather_forecast = weather_forecast_repository.get_weather_forecast(
                original_weather_forecast[column_names.TIMESTAMP].min(),
                original_weather_forecast[column_names.TIMESTAMP].max() + self.time_tick
            )
        assert original_weather_forecast.to_dict("records") == loaded_weather_forecast.to_dict("records")
        older_forecast_timestamp = original_weather_forecast[column_names.TIMESTAMP].median()
        weather_forecast_update_service.drop_weather_forecast_older_than(older_forecast_timestamp)
        with session_factory.begin():
            loaded_weather_forecast = weather_forecast_repository.get_weather_forecast(
                original_weather_forecast[column_names.TIMESTAMP].min(),
                original_weather_forecast[column_names.TIMESTAMP].max() + self.time_tick
            )
        assert not loaded_weather_forecast.empty
        assert loaded_weather_forecast[column_names.TIMESTAMP].min() >= older_forecast_timestamp
