from datetime import datetime
from typing import Iterator, Callable, Union

import pandas as pd
from boiler.constants import column_names
from dateutil import tz
from sqlalchemy import select, delete
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql import functions

from backend.models.db import TempRequirements


class TempRequirementsRepository:

    def __init__(self, db_session_provider: Callable) -> None:
        self._db_session_provider = db_session_provider

    def get_temp_requirements(self,
                              heating_obj_type: str,
                              circuit_type: str,
                              start_timestamp: datetime,
                              end_timestamp: datetime
                              ) -> pd.DataFrame:
        session = self._db_session_provider()
        statement = select(TempRequirements).filter(
            and_(
                TempRequirements.timestamp >= start_timestamp.astimezone(tz.UTC),
                TempRequirements.timestamp < end_timestamp.astimezone(tz.UTC),
                TempRequirements.circuit_type == circuit_type,
                TempRequirements.heating_obj_type == heating_obj_type
            )
        ).order_by(TempRequirements.timestamp)
        temp_requirements_iterator: Iterator[TempRequirements] = session.execute(statement).scalars()
        temp_requirements_list = []
        for record in temp_requirements_iterator:
            temp_requirements_list.append({
                column_names.TIMESTAMP: record.timestamp.replace(tzinfo=tz.UTC),
                column_names.FORWARD_TEMP: record.forward_temp,
                column_names.BACKWARD_TEMP: record.backward_temp
            })
        temp_requirements_df = pd.DataFrame(temp_requirements_list)
        return temp_requirements_df

    def add_temp_requirements(self,
                              heating_obj_type: str,
                              circuit_type: str,
                              temp_requirements_df: pd.DataFrame
                              ) -> None:
        session = self._db_session_provider()

        adding_timestamps = temp_requirements_df[column_names.TIMESTAMP].copy()
        adding_timestamps = adding_timestamps.dt.tz_convert(tz.UTC)
        adding_timestamps = adding_timestamps.dt.to_pydatetime()
        statement = delete(TempRequirements).where(
            and_(
                TempRequirements.timestamp.in_(adding_timestamps),
                TempRequirements.circuit_type == circuit_type,
                TempRequirements.heating_obj_type == heating_obj_type
            )
        )
        session.execute(statement)

        for _, row in temp_requirements_df.iterrows():
            new_record = TempRequirements(
                timestamp=row[column_names.TIMESTAMP].tz_convert(tz.UTC),
                circuit_type=circuit_type,
                heating_obj_type=heating_obj_type,
                forward_temp=row[column_names.FORWARD_TEMP],
                backward_temp=row[column_names.BACKWARD_TEMP]
            )
            session.add(new_record)

    def drop_temp_requirements_older_than(self, timestamp: datetime) -> None:
        session = self._db_session_provider()
        statement = delete(TempRequirements).where(TempRequirements.timestamp < timestamp)
        session.execute(statement)

    def get_max_cached_timestamp(self, heating_obj_type, circuit_type) -> Union[datetime, None]:
        session = self._db_session_provider()
        statement = select(TempRequirements.timestamp, functions.max(TempRequirements.timestamp)).where(
            and_(
                TempRequirements.heating_obj_type == heating_obj_type,
                TempRequirements.circuit_type == circuit_type
            )
        )
        max_timestamp = session.execute(statement).scalars().first()
        if max_timestamp is not None:
            max_timestamp = max_timestamp.replace(tzinfo=tz.UTC)
        return max_timestamp
