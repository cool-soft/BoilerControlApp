from dependency_injector import containers, providers

from boiler.temp_graph.repository.online_soft_m_temp_graph_repository import OnlineSoftMTempGraphRepository
from boiler.temp_graph.parsers.soft_m_temp_graph_parser import SoftMTempGraphParser
from backend.services.temp_graph_service.temp_graph_service_with_cache import TempGraphServiceWithCache


class OnlineTempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_parser = providers.Singleton(SoftMTempGraphParser)

    temp_graph_provider = providers.Singleton(
        OnlineSoftMTempGraphRepository,
        temp_graph_parser=temp_graph_parser
    )

    temp_graph_service = providers.Singleton(
        TempGraphServiceWithCache,
        update_interval=config.update_interval,
        temp_graph_provider=temp_graph_provider
    )
