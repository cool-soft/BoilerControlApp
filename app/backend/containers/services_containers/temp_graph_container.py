from boiler_softm.temp_graph.io.soft_m_async_temp_graph_online_loader \
    import SoftMAsyncTempGraphOnlineLoader
from boiler_softm.temp_graph.io.soft_m_sync_temp_graph_json_reader import SoftMSyncTempGraphJSONReader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Dependency

from backend.services.temp_graph_update_service.simple_temp_graph_update_service \
    import SimpleTempGraphUpdateService


class TempGraphContainer(DeclarativeContainer):
    temp_graph_repository = Dependency()

    temp_graph_reader = Factory(SoftMSyncTempGraphJSONReader)
    temp_graph_loader = Factory(
        SoftMAsyncTempGraphOnlineLoader,
        reader=temp_graph_reader
    )
    temp_graph_update_service = Factory(
        SimpleTempGraphUpdateService,
        temp_graph_loader=temp_graph_loader,
        temp_graph_dumper=temp_graph_repository
    )
