from dependency_injector import containers, providers

from boiler.temp_graph.io.sync.sync_temp_graph_in_memory_dumper_loader \
    import SyncTempGraphInMemoryDumperLoader
from boiler_softm.temp_graph.io.sync.soft_m_sync_temp_graph_json_reader import SoftMSyncTempGraphJSONReader
from boiler_softm.temp_graph.io.async_.soft_m_async_temp_graph_online_loader \
    import SoftMAsyncTempGraphOnlineLoader
from backend.services.temp_graph_update_service.simple_temp_graph_update_service \
    import SimpleTempGraphUpdateService


class TempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_reader = providers.Singleton(SoftMSyncTempGraphJSONReader)

    temp_graph_loader = providers.Singleton(SoftMAsyncTempGraphOnlineLoader,
                                            reader=temp_graph_reader)

    temp_graph_dumper_loader = providers.Singleton(SyncTempGraphInMemoryDumperLoader)

    temp_graph_update_service = providers.Singleton(SimpleTempGraphUpdateService,
                                                    temp_graph_loader=temp_graph_loader,
                                                    temp_graph_dumper=temp_graph_dumper_loader)
