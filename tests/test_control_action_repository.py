from datetime import datetime
from random import random, randint

import pandas as pd
import pytest
from dateutil import tz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from boiler.constants import column_names, circuit_types

from backend.models.db import ControlAction
from backend.repositories.control_action_repository import ControlActionRepository


class TestControlActionRepository:
    time_tick = pd.Timedelta(seconds=300)
    weather_data_timezone = tz.gettz("Asia/Yekaterinburg")
    action_start_timestamp = datetime.now(tz=weather_data_timezone)
    action_end_timestamp = action_start_timestamp + (100 * time_tick)
    control_action_drop_timestamp = action_start_timestamp + (10 * time_tick)
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
        return ControlActionRepository(session_factory)

    @pytest.fixture
    def control_action_df(self):
        forecast_list = []
        for circuit_type in self.circuits:
            current_timestamp = self.action_start_timestamp
            while current_timestamp < self.action_end_timestamp:
                forecast_list.append({
                    column_names.TIMESTAMP: current_timestamp,
                    column_names.CIRCUIT_TYPE: circuit_type,
                    column_names.FORWARD_PIPE_COOLANT_TEMP: random()
                })
                current_timestamp += self.time_tick
        forecast_df = pd.DataFrame(forecast_list)
        return forecast_df

    def test_set_get(self, control_action_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_control_action(control_action_df)
            session.commit()
        with session_factory.begin():
            for circuit_type in self.circuits:
                loaded_control_action = repository.get_control_action_by_timestamp_range(
                    control_action_df[column_names.TIMESTAMP].min(),
                    control_action_df[column_names.TIMESTAMP].max() + self.time_tick,
                    circuit_type
                )
                original_control_action = control_action_df[
                    control_action_df[column_names.CIRCUIT_TYPE] == circuit_type
                    ].copy()
                assert loaded_control_action.to_dict("records") == original_control_action.to_dict("records")
        session_factory.remove()

    def test_set_drop_get(self, control_action_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_control_action(control_action_df)
            session.commit()
        with session_factory.begin() as session:
            repository.drop_control_action_older_than(self.control_action_drop_timestamp, circuit_types.HEATING)
            session.commit()
        with session_factory.begin():
            loaded_control_action = repository.get_control_action_by_timestamp_range(
                control_action_df[column_names.TIMESTAMP].min(),
                control_action_df[column_names.TIMESTAMP].max() + self.time_tick,
                circuit_types.HEATING
            )
        session_factory.remove()
        assert not loaded_control_action.empty
        assert (control_action_df.columns == loaded_control_action.columns).all()
        assert loaded_control_action[column_names.TIMESTAMP].min() >= self.control_action_drop_timestamp

    def test_set_with_update(self, control_action_df, repository, session_factory):
        with session_factory.begin() as session:
            repository.add_control_action(control_action_df)
            session.commit()

        selected_circuit = self.circuits[0]
        new_control_action_df = control_action_df[
            control_action_df[column_names.CIRCUIT_TYPE] == selected_circuit
            ].copy()
        index_count = len(new_control_action_df.index)
        for i in range(3):
            random_index = new_control_action_df.index[randint(0, index_count - 1)]
            new_control_action_df.at[random_index, column_names.FORWARD_PIPE_COOLANT_TEMP] = random()
        with session_factory.begin() as session:
            repository.add_control_action(new_control_action_df)
            session.commit()

        with session_factory.begin():
            loaded_control_action = repository.get_control_action_by_timestamp_range(
                control_action_df[column_names.TIMESTAMP].min(),
                control_action_df[column_names.TIMESTAMP].max() + self.time_tick,
                selected_circuit
            )
            assert new_control_action_df.to_dict("records") == loaded_control_action.to_dict("records")

            for circuit_type in self.circuits[1:]:
                loaded_control_action = repository.get_control_action_by_timestamp_range(
                    control_action_df[column_names.TIMESTAMP].min(),
                    control_action_df[column_names.TIMESTAMP].max() + self.time_tick,
                    circuit_type
                )
                original_control_action = control_action_df[
                    control_action_df[column_names.CIRCUIT_TYPE] == circuit_type
                    ].copy()
                assert original_control_action.to_dict("records") == loaded_control_action.to_dict("records")

        session_factory.remove()
