from typing import Iterator, Callable

import pandas as pd
from sqlalchemy import select, delete
from boiler.constants import column_names

from backend.models.db import TempGraphDBModel


class TempGraphRepository:

    def __init__(self, db_session_provider: Callable) -> None:
        self._db_session_provider = db_session_provider

    def get_temp_graph_for_circuit_type(self, circuit_type: str) -> pd.DataFrame:
        session = self._db_session_provider()
        statement = select(TempGraphDBModel).filter(
            TempGraphDBModel.circuit_type == circuit_type,
        ).order_by(TempGraphDBModel.weather_temp)
        temp_graph_iterator: Iterator[TempGraphDBModel] = session.execute(statement).scalars()
        temp_graph_list = []
        for record in temp_graph_iterator:
            temp_graph_list.append({
                column_names.WEATHER_TEMP: record.weather_temp,
                column_names.FORWARD_TEMP: record.forward_temp,
                column_names.BACKWARD_TEMP: record.backward_temp
            })
        temp_graph_df = pd.DataFrame(temp_graph_list)
        return temp_graph_df

    def set_temp_graph_for_circuit_type(self, temp_graph_df: pd.DataFrame, circuit_type: str) -> None:
        session = self._db_session_provider()

        statement = delete(TempGraphDBModel).where(TempGraphDBModel.circuit_type == circuit_type)
        session.execute(statement)

        for _, row in temp_graph_df.iterrows():
            new_record = TempGraphDBModel(
                weather_temp=row[column_names.WEATHER_TEMP],
                circuit_type=circuit_type,
                forward_temp=row[column_names.FORWARD_TEMP],
                backward_temp=row[column_names.BACKWARD_TEMP]
            )
            session.add(new_record)
