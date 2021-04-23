from dependency_injector import containers, providers

from boiler.temp_graph.repository.stream.async_.temp_graph_stream_async_fake_repository \
    import TempGraphStreamAsyncFakeRepository
from boiler_softm.temp_graph.parsers.soft_m_json_temp_graph_parser import SoftMJSONTempGraphParser
from boiler_softm.temp_graph.repository.stream.async_.soft_m_online_stream_async_temp_graph_repository \
    import SoftMOnlineStreamAsyncTempGraphRepository
from backend.services.temp_graph_update_service.simple_temp_graph_update_service import SimpleTempGraphUpdateService


class TempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_parser = providers.Singleton(SoftMJSONTempGraphParser)

    temp_graph_src_repository = providers.Singleton(SoftMOnlineStreamAsyncTempGraphRepository,
                                                    temp_graph_parser=temp_graph_parser)

    temp_graph_repository = providers.Singleton(TempGraphStreamAsyncFakeRepository)

    temp_graph_update_service = providers.Singleton(SimpleTempGraphUpdateService,
                                                    temp_graph_src_repository=temp_graph_src_repository,
                                                    temp_graph_repository=temp_graph_repository)
