from dependency_injector import containers, providers

from .services_containers.control_action_container import ControlActionContainer
from .services_containers.dynamic_settings_container import DynamicSettingsContainer
from .services_containers.temp_graph_container import TempGraphContainer
from .services_containers.temp_requirements_container import TempRequirementsContainer
from .services_containers.updater_container import UpdateContainer


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    dynamic_settings_pkg = providers.Container(
        DynamicSettingsContainer,
        config=config.dynamic_settings
    )

    temp_graph_pkg = providers.Container(
        TempGraphContainer,
        config=config.temp_graph_providing
    )

    temp_requirements_pkg = providers.Container(
        TempRequirementsContainer,
        config=config.temp_requirements_calculation,
        temp_graph_repository=temp_graph_pkg.temp_graph_repository
    )

    control_action_pkg = providers.Container(
        ControlActionContainer,
        config=config.boiler_temp_prediction,
        settings_service=dynamic_settings_pkg.settings_service,
        temp_requirements_repository=temp_requirements_pkg.temp_requirements_repository
    )

    updater_pkg = providers.Container(
        UpdateContainer,
        config=config.updater,
        control_actions_predictor=control_action_pkg.temp_prediction_service,
        temp_graph_updater=temp_graph_pkg.temp_graph_update_service,
        temp_requirements_calculator=temp_requirements_pkg.temp_requirements_service,
    )
