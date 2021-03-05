from dependency_injector import containers, providers

from services.temp_graph_service.online_soft_m_temp_graph_service import OnlineSoftMTempGraphService
from heating_system.temp_graph_utils.temp_graph_parsers import SoftMTempGraphParser


class OnlineTempGraphContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_parser = providers.Singleton(SoftMTempGraphParser)

    temp_graph_service = providers.Singleton(
        OnlineSoftMTempGraphService,
        server_address=config.server_address,
        update_interval=config.update_interval,
        temp_graph_parser=temp_graph_parser
    )
