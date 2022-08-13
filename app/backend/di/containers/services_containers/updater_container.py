from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.updatable_items.control_action_updatable_item import ControlActionUpdatableItem


class UpdateContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    control_actions_predictor = Dependency()

    control_action_updatable_item = Singleton(
        ControlActionUpdatableItem,
        provider=control_actions_predictor.provider,
    )
    # TODO: очистка старого control action

    updater_service = Singleton(
        SyncUpdaterService,
        item_to_update=control_action_updatable_item
    )
