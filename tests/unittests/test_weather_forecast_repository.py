from datetime import datetime
from random import random, randint

import pandas as pd
import pytest
from boiler.constants import column_names
from dateutil.tz import gettz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import WeatherForecast
from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class TestWeatherForecastRepository:
    time_tick = pd.Timedelta(seconds=300)
    weather_data_timezone = gettz("Asia/Yekaterinburg")
    forecast_start_timestamp = datetime.now(tz=weather_data_timezone)
    forecast_end_timestamp = forecast_start_timestamp + (100 * time_tick)
    forecast_drop_timestamp = forecast_start_timestamp + (10 * time_tick)

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
    def repository(self, session_factory):
        return WeatherForecastRepository(session_factory)

    @pytest.fixture
    def weather_forecast_df(self):
        forecast_list = []
        current_timestamp = self.forecast_start_timestamp
        while current_timestamp < self.forecast_end_timestamp:
            forecast_list.append(
                {
                    column_names.TIMESTAMP: current_timestamp,
                    column_names.WEATHER_TEMP: random()
                }
            )
            current_timestamp += self.time_tick
        forecast_df = pd.DataFrame(forecast_list)
        return forecast_df

    def test_set_get(self, weather_forecast_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_weather_forecast(weather_forecast_df)
            session.commit()
        with session_factory.begin():
            loaded_weather_forecast = repository.get_weather_forecast(
                weather_forecast_df[column_names.TIMESTAMP].min(),
                weather_forecast_df[column_names.TIMESTAMP].max() + self.time_tick
            )
        session_factory.remove()
        assert weather_forecast_df.to_dict("records") == loaded_weather_forecast.to_dict("records")

    def test_set_drop_get(self, weather_forecast_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_weather_forecast(weather_forecast_df)
            session.commit()
        session_factory.remove()
        with session_factory.begin() as session:
            repository.drop_weather_forecast_older_than(self.forecast_drop_timestamp)
            session.commit()
        session_factory.remove()
        with session_factory.begin():
            loaded_weather_forecast = repository.get_weather_forecast(
                weather_forecast_df[column_names.TIMESTAMP].min(),
                weather_forecast_df[column_names.TIMESTAMP].max() + self.time_tick
            )
        session_factory.remove()
        assert not loaded_weather_forecast.empty
        assert (weather_forecast_df.columns == loaded_weather_forecast.columns).all()
        assert loaded_weather_forecast[column_names.TIMESTAMP].min() >= self.forecast_drop_timestamp

    def test_set_with_update(self, weather_forecast_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_weather_forecast(weather_forecast_df)
            session.commit()

        new_weather_forecast_df = weather_forecast_df.copy()
        index_count = len(new_weather_forecast_df.index)
        for i in range(3):
            random_index = new_weather_forecast_df.index[randint(0, index_count-1)]
            new_weather_forecast_df.at[random_index, column_names.WEATHER_TEMP] = random()
        with session_factory.begin() as session:
            repository.add_weather_forecast(new_weather_forecast_df)
            session.commit()

        with session_factory.begin():
            loaded_weather_forecast = repository.get_weather_forecast(
                new_weather_forecast_df[column_names.TIMESTAMP].min(),
                new_weather_forecast_df[column_names.TIMESTAMP].max() + self.time_tick
            )

        session_factory.remove()
        assert new_weather_forecast_df.to_dict("records") == loaded_weather_forecast.to_dict("records")

    def test_get_max_timestamp(self, weather_forecast_df, repository, session_factory):
        with session_factory.begin():
            max_cached_timestamp = repository.get_max_cached_timestamp()
            assert max_cached_timestamp is None

        with session_factory.begin() as session:
            repository.add_weather_forecast(weather_forecast_df)
            session.commit()
        with session_factory.begin():
            max_cached_timestamp = repository.get_max_cached_timestamp()
            assert max_cached_timestamp == weather_forecast_df[column_names.TIMESTAMP].max()

        session_factory.remove()