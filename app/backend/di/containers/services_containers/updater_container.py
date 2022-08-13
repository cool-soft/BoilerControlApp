from datetime import timedelta

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration, Callable
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.updatable_items.control_action_updatable_item import ControlActionUpdatableItem


class UpdateContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    control_actions_predictor = Dependency()

    control_action_updatable_item = Singleton(
        ControlActionUpdatableItem,
        provider=control_actions_predictor.provider,
        update_interval=Callable(timedelta, seconds=config.control_action_update_interval)
    )
    # TODO: очистка старого control action

    updater_service = Singleton(
        SyncUpdaterService,
        item_to_update=control_action_updatable_item
    )
