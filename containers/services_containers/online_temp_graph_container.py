from dependency_injector import containers, providers

from temp_requirements.temp_graph_providers.online_soft_m_temp_graph_provider import OnlineSoftMTempGraphProvider
from temp_requirements.temp_graph_parsers.soft_m_temp_graph_parser import SoftMTempGraphParser


class OnlineTempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_parser = providers.Singleton(SoftMTempGraphParser)

    temp_graph_service = providers.Singleton(
        OnlineSoftMTempGraphProvider,
        update_interval=config.update_interval,
        temp_graph_parser=temp_graph_parser
    )
