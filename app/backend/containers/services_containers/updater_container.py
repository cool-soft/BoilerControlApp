from dependency_injector import containers, providers

from backend.services.updater_service.simple_updater_service import SimpleUpdaterService


class UpdateContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    control_actions_predictor = providers.Dependency()
    temp_graph_updater = providers.Dependency()
    temp_requirements_calculator = providers.Dependency()

    updater_service = providers.Singleton(SimpleUpdaterService,
                                          control_action_predictor_provider=control_actions_predictor.provider,
                                          temp_graph_updater_provider=temp_graph_updater.provider,
                                          temp_requirements_calculator_provider=temp_requirements_calculator.provider,
                                          temp_graph_update_interval=config.temp_graph_update_interval,
                                          control_action_update_interval=config.control_action_update_interval)
