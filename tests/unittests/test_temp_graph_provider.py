from datetime import timedelta, datetime
from time import sleep

import pandas as pd
import pytest
from boiler.constants import circuit_types
from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from dateutil import tz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from updater_keychain.keychain_item import UpdaterKeychain

from backend.models.db import TempGraph
from backend.providers.temp_graph_provider import TempGraphProvider
from backend.repositories.temp_graph_repository import TempGraphRepository


class TestTempGraphProvider:
    db_url = "sqlite:///:memory:"
    circuit_type = circuit_types.HEATING

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            TempGraph.metadata.drop_all(conn)
            TempGraph.metadata.create_all(conn)
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
    def updater_keychain(self):
        return UpdaterKeychain(
            update_interval=timedelta(minutes=10)
        )

    @pytest.fixture
    def provider(self, temp_graph_loader, session_factory, repository, updater_keychain):
        return TempGraphProvider(
            temp_graph_loader,
            session_factory,
            repository,
            updater_keychain,
            self.circuit_type
        )

    def test_provide_temp_graph(self, provider, session_factory, repository, updater_keychain):
        start_datetime = datetime.now(tz=tz.UTC)
        temp_graph_from_server = provider.load_temp_graph()
        assert isinstance(temp_graph_from_server, pd.DataFrame)
        assert not temp_graph_from_server.empty
        assert updater_keychain.get_last_update_datetime() >= start_datetime

        with session_factory():
            temp_graph = repository.get_temp_graph_for_circuit_type(self.circuit_type)
        assert not temp_graph.empty
        session_factory.remove()

        sleep(0.1)
        datetime_now = datetime.now(tz=tz.UTC)
        temp_graph_from_cache = provider.load_temp_graph()
        assert isinstance(temp_graph_from_cache, pd.DataFrame)
        assert not temp_graph_from_cache.empty
        assert updater_keychain.get_last_update_datetime() < datetime_now
