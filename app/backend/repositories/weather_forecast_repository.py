from datetime import datetime
from typing import Iterator, Callable, Union

import pandas as pd
from boiler.constants import column_names
from dateutil import tz
from sqlalchemy import select, delete
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql import functions

from backend.models.db import WeatherForecast


class WeatherForecastRepository:

    def __init__(self, db_session_provider: Callable) -> None:
        self._db_session_provider = db_session_provider

    def get_weather_forecast(self,
                             start_timestamp: datetime,
                             end_timestamp: datetime
                             ) -> pd.DataFrame:
        session = self._db_session_provider()
        statement = select(WeatherForecast).filter(
            and_(
                WeatherForecast.timestamp >= start_timestamp.astimezone(tz.UTC),
                WeatherForecast.timestamp < end_timestamp.astimezone(tz.UTC)
            )
        ).order_by(WeatherForecast.timestamp)
        weather_forecast_iterator: Iterator[WeatherForecast] = session.execute(statement).scalars()
        weather_forecast_list = []
        for record in weather_forecast_iterator:
            weather_forecast_list.append({
                column_names.TIMESTAMP: record.timestamp.replace(tzinfo=tz.UTC),
                column_names.WEATHER_TEMP: record.weather_temp
            })
        weather_forecast_df = pd.DataFrame(weather_forecast_list)
        return weather_forecast_df

    def add_weather_forecast(self, weather_df: pd.DataFrame) -> None:
        session = self._db_session_provider()

        adding_timestamps = weather_df[column_names.TIMESTAMP].copy()
        adding_timestamps = adding_timestamps.dt.tz_convert(tz.UTC)
        adding_timestamps = adding_timestamps.dt.to_pydatetime()
        statement = delete(WeatherForecast).where(WeatherForecast.timestamp.in_(adding_timestamps))
        session.execute(statement)

        for _, row in weather_df.iterrows():
            new_record = WeatherForecast(
                timestamp=row[column_names.TIMESTAMP].tz_convert(tz.UTC),
                weather_temp=row[column_names.WEATHER_TEMP]
            )
            session.add(new_record)

    def drop_weather_forecast_older_than(self, timestamp: datetime) -> None:
        session = self._db_session_provider()
        statement = delete(WeatherForecast).where(WeatherForecast.timestamp < timestamp)
        session.execute(statement)

    def get_max_cached_timestamp(self) -> Union[datetime, None]:
        session = self._db_session_provider()
        statement = select(WeatherForecast.timestamp, functions.max(WeatherForecast.timestamp))
        max_timestamp = session.execute(statement).scalars().first()
        if max_timestamp is not None:
            max_timestamp = max_timestamp.replace(tzinfo=tz.UTC)
        return max_timestamp
