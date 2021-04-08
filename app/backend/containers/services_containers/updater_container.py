import pandas as pd
from dependency_injector import containers, providers

from updater_service.simple_updater_service import SimpleUpdaterService
from backend.services.control_action_prediction_service.control_action_updatable_item import ControlActionUpdatableItem
from backend.services.temp_graph_update_service.temp_graph_updatable_item import TempGraphUpdatableItem
from backend.services.temp_requirements_update_service.temp_requirements_updatable_item import \
    TempRequirementsUpdatableItem


class UpdateContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    control_actions_predictor = providers.Dependency()
    temp_graph_updater = providers.Dependency()
    temp_requirements_calculator = providers.Dependency()

    temp_graph_update_interval = providers.Callable(pd.Timedelta,
                                                    seconds=config.temp_graph_update_interval)
    temp_graph_updatable_item = providers.Singleton(TempGraphUpdatableItem,
                                                    provider=temp_graph_updater.provider,
                                                    update_interval=temp_graph_update_interval)

    temp_requirements_update_interval = providers.Callable(pd.Timedelta,
                                                           seconds=config.temp_requirements_update_interval)
    temp_requirements_updatable_item = providers.Singleton(TempRequirementsUpdatableItem,
                                                           provider=temp_requirements_calculator.provider,
                                                           update_interval=temp_requirements_update_interval)

    control_action_updatable_item = providers.Singleton(ControlActionUpdatableItem,
                                                        provider=control_actions_predictor.provider,
                                                        dependencies=providers.List(
                                                            temp_graph_updatable_item,
                                                            temp_requirements_updatable_item
                                                        ))

    updater_service = providers.Singleton(SimpleUpdaterService,
                                          item_to_update=control_action_updatable_item)
