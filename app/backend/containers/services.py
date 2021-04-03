from dependency_injector import containers, providers

from .services_containers.control_action_container import ControlActionContainer
from .services_containers.temp_graph_container import TempGraphContainer
from .services_containers.temp_requirements_container import TempRequirementsContainer


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_providing = providers.Container(
        TempGraphContainer,
        config=config.temp_graph_providing
    )

    temp_requirements_calculation = providers.Container(
        TempRequirementsContainer,
        config=config.temp_requirements_calculation,
        temp_graph_service=temp_graph_providing.temp_graph_service
    )

    boiler_temp_prediction = providers.Container(
        ControlActionContainer,
        config=config.boiler_temp_prediction,
        temp_requirements_repository=temp_requirements_calculation.temp_requirements_repository
    )
