from datetime import timedelta

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration, Callable, Factory
from updater.update_datetime_memento.update_datetime_memento import UpdateDatetimeMementoWithDBRepo
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.constants import keychain_names
from backend.updatable_items.control_action_updatable_item import ControlActionUpdatableItem


class UpdateContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    control_actions_predictor = Dependency()
    db_session_provider = Dependency()
    keychain_repository = Dependency()

    control_action_updatable_item = Singleton(
        ControlActionUpdatableItem,
        provider=control_actions_predictor.provider,
        update_interval=Callable(timedelta, seconds=config.control_action_update_interval),
        update_datetime_memento=Factory(
            UpdateDatetimeMementoWithDBRepo,
            db_session_factory=db_session_provider,
            memento_name=keychain_names.CONTROL_ACTION_UPDATE_KEYCHAIN_NAME,
            update_datetime_repository=keychain_repository,
        )
    )
    # TODO: очистка старого control action

    updater_service = Singleton(
        SyncUpdaterService,
        item_to_update=control_action_updatable_item
    )
