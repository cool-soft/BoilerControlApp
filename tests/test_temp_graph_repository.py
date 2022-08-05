from random import random

import pandas as pd
import pytest
from boiler.constants import column_names, circuit_types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import ControlAction
from backend.repositories.temp_graph_repository import TempGraphRepository


class TestTempGraphRepository:
    temp_graph_rows_count = 5
    circuits = [circuit_types.HEATING, circuit_types.HOT_WATER]

    db_url = "sqlite:///:memory:"

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            ControlAction.metadata.drop_all(conn)
            ControlAction.metadata.create_all(conn)
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
        return TempGraphRepository(session_factory)

    @pytest.fixture
    def temp_graph_dfs(self):
        temp_graphs = {}
        for circuit_type in self.circuits:
            temp_graph_list = []
            for i in range(self.temp_graph_rows_count):
                temp_graph_list.append({
                    column_names.WEATHER_TEMP: random(),
                    column_names.FORWARD_PIPE_COOLANT_TEMP: random(),
                    column_names.BACKWARD_PIPE_COOLANT_TEMP: random()
                })
            temp_graph_list = sorted(temp_graph_list, key=lambda x: x[column_names.WEATHER_TEMP])
            temp_graphs[circuit_type] = pd.DataFrame(temp_graph_list)
        return temp_graphs

    def test_set_get(self, temp_graph_dfs, repository, session_factory):
        with session_factory.begin() as session:
            for circuit_type, temp_graph in temp_graph_dfs.items():
                repository.set_temp_graph_for_circuit_type(temp_graph, circuit_type)
            session.commit()
        with session_factory.begin():
            for circuit_type in self.circuits:
                loaded_temp_graph = repository.get_temp_graph_for_circuit_type(circuit_type)
                assert loaded_temp_graph.to_dict("records") == \
                       temp_graph_dfs[circuit_type].to_dict("records")
        session_factory.remove()
