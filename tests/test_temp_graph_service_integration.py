from random import random

import pandas as pd
import pytest
from boiler.constants import column_names, circuit_types
from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import ControlAction
from backend.repositories.temp_graph_repository import TempGraphRepository
from backend.services.temp_graph_update_service import TempGraphUpdateService


class TestTempGraphServiceIntegration:
    db_url = "sqlite:///:memory:"
    circuit_type = circuit_types.HEATING

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
    def temp_graph_reader(self):
        return SoftMLysvaSyncTempGraphOnlineReader()

    @pytest.fixture
    def temp_graph_loader(self, temp_graph_reader, is_need_proxy, proxy_address):
        http_proxy = None
        https_proxy = None
        if is_need_proxy:
            http_proxy = proxy_address
            https_proxy = proxy_address
        return SoftMLysvaSyncTempGraphOnlineLoader(
            reader=temp_graph_reader,
            http_proxy=http_proxy,
            https_proxy=https_proxy
        )

    @pytest.fixture
    def repository(self, session_factory):
        return TempGraphRepository(session_factory)

    @pytest.fixture
    def service(self, session_factory, repository, temp_graph_loader):
        return TempGraphUpdateService(
            session_factory,
            repository,
            temp_graph_loader,
            self.circuit_type
        )

    def test_update_temp_graph(self, repository, session_factory, service):
        service.update_temp_graph()

        with session_factory():
            temp_graph: pd.DataFrame = repository.get_temp_graph_for_circuit_type(self.circuit_type)
        assert not temp_graph.empty

        session_factory.remove()
