from boiler.constants import circuit_types
from boiler.temp_graph.io.abstract_sync_temp_graph_loader import AbstractSyncTempGraphLoader
from sqlalchemy.orm import scoped_session

from backend.repositories.temp_graph_repository import TempGraphRepository


class TempGraphUpdateService:

    def __init__(self,
                 db_session_factory: scoped_session,
                 temp_graph_repository: TempGraphRepository,
                 temp_graph_loader: AbstractSyncTempGraphLoader,
                 circuit_type: str = circuit_types.HEATING
                 ) -> None:
        self._session_factory = db_session_factory
        self._temp_graph_repository = temp_graph_repository
        self._temp_graph_loader = temp_graph_loader
        self._circuit_type = circuit_type

    def update_temp_graph(self) -> None:
        temp_graph_df = self._temp_graph_loader.load_temp_graph()
        with self._session_factory() as session:
            self._temp_graph_repository.set_temp_graph_for_circuit_type(
                temp_graph_df,
                self._circuit_type
            )
            session.commit()
        self._session_factory.remove()
