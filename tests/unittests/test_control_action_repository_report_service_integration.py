from datetime import datetime
from random import random

import pandas as pd
import pytest
from boiler.constants import column_names, circuit_types
from dateutil import tz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.api import ControlActionAPIModel
from backend.models.db import ControlActionDBModel
from backend.repositories.control_action_repository import ControlActionRepository
from backend.services.control_action_service import ControlActionService


class TestControlActionRepository:
    time_tick = pd.Timedelta(seconds=300)
    weather_data_timezone = tz.gettz("Asia/Yekaterinburg")
    action_start_timestamp = datetime.now(tz=weather_data_timezone)
    action_end_timestamp = action_start_timestamp + (100 * time_tick)
    control_action_drop_timestamp = action_start_timestamp + (10 * time_tick)
    circuits = [circuit_types.HEATING, circuit_types.HOT_WATER]
    v1_pattern = "%Y-%m-%d %H:%M"

    db_url = "sqlite:///:memory:"

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            ControlActionDBModel.metadata.drop_all(conn)
            ControlActionDBModel.metadata.create_all(conn)
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
                    column_names.FORWARD_TEMP: random()
                })
                current_timestamp += self.time_tick
        forecast_df = pd.DataFrame(forecast_list)
        return forecast_df

    @pytest.fixture
    def report_service(self, repository, session_factory):
        return ControlActionService(db_session_provider=session_factory, control_action_repository=repository)

    def test_report(self, control_action_df, repository, session_factory, report_service):
        with session_factory.begin() as session:
            repository.add_control_action(control_action_df)
            session.commit()

        control_action_df = control_action_df[
            control_action_df[column_names.CIRCUIT_TYPE] == circuit_types.HEATING
            ].copy()

        report = report_service.report(self.action_start_timestamp, self.action_end_timestamp)
        assert isinstance(report, list)
        assert len(report) == len(control_action_df)
        for row in report:
            assert isinstance(row, ControlActionAPIModel)

        session_factory.remove()
