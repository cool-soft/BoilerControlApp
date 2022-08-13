from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Factory

from backend.repositories.temp_graph_repository import TempGraphRepository
from backend.providers.temp_graph_provider import TempGraphUpdateService


class TempGraphContainer(DeclarativeContainer):
    db_session_provider = Dependency()

    temp_graph_repository = Singleton(
        TempGraphRepository,
        db_session_provider=db_session_provider
    )
    temp_graph_reader = Factory(SoftMLysvaSyncTempGraphOnlineReader)
    temp_graph_loader = Factory(
        SoftMLysvaSyncTempGraphOnlineLoader,
        reader=temp_graph_reader
    )
    temp_graph_update_service = Singleton(
        TempGraphUpdateService,
        db_session_factory=db_session_provider,
        temp_graph_loader=temp_graph_loader,
        temp_graph_repository=temp_graph_repository
    )
