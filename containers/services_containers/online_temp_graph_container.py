from dependency_injector import containers, providers

from boiler.temp_graph.providers.online_soft_m_temp_graph_provider import OnlineSoftMTempGraphProvider
from boiler.temp_graph.parsers.soft_m_temp_graph_parser import SoftMTempGraphParser
from services.temp_graph_service.temp_graph_service_with_cache import TempGraphServiceWithCache


class OnlineTempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_parser = providers.Singleton(SoftMTempGraphParser)

    temp_graph_provider = providers.Singleton(
        OnlineSoftMTempGraphProvider,
        temp_graph_parser=temp_graph_parser
    )

    temp_graph_service = providers.Singleton(
        TempGraphServiceWithCache,
        update_interval=config.update_interval,
        temp_graph_provider=temp_graph_provider
    )
