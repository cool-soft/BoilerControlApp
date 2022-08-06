from datetime import datetime
from typing import Iterator

import pandas as pd
from boiler.constants import column_names
from dateutil import tz
from sqlalchemy import select, delete
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.elements import and_

from backend.models.db import ControlAction


class ControlActionRepository:

    def __init__(self, db_session_provider: scoped_session) -> None:
        self._db_session_provider = db_session_provider

    def get_control_action(self,
                           start_timestamp: datetime,
                           end_timestamp: datetime,
                           circuit_type: str
                           ) -> pd.DataFrame:
        session = self._db_session_provider()
        statement = select(ControlAction).filter(
            and_(
                ControlAction.timestamp >= start_timestamp.astimezone(tz.UTC),
                ControlAction.timestamp < end_timestamp.astimezone(tz.UTC),
                ControlAction.circuit_type == circuit_type
            )
        ).order_by(ControlAction.timestamp)
        control_action_iterator: Iterator[ControlAction] = session.execute(statement).scalars()
        control_action_list = []
        for record in control_action_iterator:
            control_action_list.append({
                column_names.TIMESTAMP: record.timestamp.replace(tzinfo=tz.UTC),
                column_names.CIRCUIT_TYPE: record.circuit_type,
                column_names.FORWARD_TEMP: record.forward_temp
            })
        control_action_df = pd.DataFrame(control_action_list)
        return control_action_df

    def add_control_action(self, control_action_df: pd.DataFrame) -> None:
        session = self._db_session_provider()

        circuit_types = control_action_df[column_names.CIRCUIT_TYPE].unique()
        for circuit_type in circuit_types:
            circuit_data = control_action_df[control_action_df[column_names.CIRCUIT_TYPE] == circuit_type]
            circuit_data_timestamps = circuit_data[column_names.TIMESTAMP]
            self._drop_by_circuit_type_and_timestamp(circuit_type, circuit_data_timestamps)

        for _, row in control_action_df.iterrows():
            new_record = ControlAction(
                timestamp=row[column_names.TIMESTAMP].tz_convert(tz.UTC),
                circuit_type=row[column_names.CIRCUIT_TYPE],
                forward_temp=row[column_names.FORWARD_TEMP]
            )
            session.add(new_record)

    def _drop_by_circuit_type_and_timestamp(self,
                                            circuit_type: str,
                                            circuit_data_timestamps: pd.Series
                                            ) -> None:
        session = self._db_session_provider()
        circuit_data_timestamps = circuit_data_timestamps.copy()
        circuit_data_timestamps = circuit_data_timestamps.dt.tz_convert(tz.UTC)
        circuit_data_timestamps = circuit_data_timestamps.dt.to_pydatetime()
        statement = delete(ControlAction).where(
            and_(
                ControlAction.timestamp.in_(circuit_data_timestamps),
                ControlAction.circuit_type == circuit_type
            ))
        session.execute(statement)

    def drop_control_action_older_than(self, timestamp: datetime, circuit_type: str) -> None:
        session = self._db_session_provider()
        statement = delete(ControlAction).where(
            and_(
                ControlAction.timestamp < timestamp,
                ControlAction.circuit_type == circuit_type
            )
        )
        session.execute(statement)
