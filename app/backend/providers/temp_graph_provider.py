from datetime import datetime

import pandas as pd
from boiler.constants import circuit_types
from dateutil import tz
from boiler.temp_graph.io.abstract_sync_temp_graph_loader import AbstractSyncTempGraphLoader
from sqlalchemy.orm import scoped_session
from updater.helpers import is_need_update_item
from updater.update_keychain import UpdateKeychain

from backend.repositories.temp_graph_repository import TempGraphRepository


class TempGraphProvider(AbstractSyncTempGraphLoader):

    def __init__(self,
                 temp_graph_loader: AbstractSyncTempGraphLoader,
                 db_session_factory: scoped_session,
                 temp_graph_repository: TempGraphRepository,
                 update_keychain: UpdateKeychain,
                 circuit_type: str = circuit_types.HEATING
                 ) -> None:
        self._temp_graph_loader = temp_graph_loader
        self._session_factory = db_session_factory
        self._temp_graph_repository = temp_graph_repository
        self._updater_keychain = update_keychain
        self._circuit_type = circuit_type

    def load_temp_graph(self) -> pd.DataFrame:
        datetime_now = datetime.now(tz=tz.UTC)
        if is_need_update_item(self._updater_keychain, datetime_now):
            temp_graph = self._temp_graph_loader.load_temp_graph()
            with self._session_factory.begin() as session:
                self._temp_graph_repository.set_temp_graph_for_circuit_type(
                    temp_graph,
                    self._circuit_type
                )
                session.commit()
            self._updater_keychain.set_last_update_datetime(datetime_now)
        else:
            with self._session_factory():
                temp_graph = self._temp_graph_repository.get_temp_graph_for_circuit_type(
                    self._circuit_type
                )
        self._session_factory.remove()
        return temp_graph
