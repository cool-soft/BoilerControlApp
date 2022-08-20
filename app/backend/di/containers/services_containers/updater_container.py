from datetime import timedelta

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration, Callable, Factory, List
from updater.update_datetime_memento.update_datetime_memento import UpdateDatetimeMementoWithDBRepo
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.constants import keychain_names
from backend.updatable_items.control_action_drop_updatable_item import ControlActionDropUpdatableItem
from backend.updatable_items.control_action_predictor_updatable_item import ControlActionPredictorUpdatableItem
from backend.updatable_items.group_updatable_item import GroupUpdatableItem


class UpdateContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    control_action_predictor_service = Dependency()
    control_action_service = Dependency()
    db_session_provider = Dependency()
    keychain_repository = Dependency()

    control_action_updatable_item = Singleton(
        ControlActionPredictorUpdatableItem,
        provider=control_action_predictor_service.provider,
        update_interval=Callable(timedelta, seconds=config.control_action_update_interval),
        update_datetime_memento=Factory(
            UpdateDatetimeMementoWithDBRepo,
            db_session_factory=db_session_provider,
            memento_name=keychain_names.CONTROL_ACTION_UPDATE_KEYCHAIN_NAME,
            update_datetime_repository=keychain_repository,
        )
    )
    control_action_drop_updatable_item = Singleton(
        ControlActionDropUpdatableItem,
        provider=control_action_service.provider,
        update_interval=Callable(timedelta, seconds=config.control_action_drop_interval),
        update_datetime_memento=Factory(
            UpdateDatetimeMementoWithDBRepo,
            db_session_factory=db_session_provider,
            memento_name=keychain_names.CONTROL_ACTION_DROP_KEYCHAIN_NAME,
            update_datetime_repository=keychain_repository,
        )
    )
    group_updatable_item = Singleton(
        GroupUpdatableItem,
        dependencies=List(control_action_drop_updatable_item, control_action_updatable_item)
    )

    updater_service = Singleton(
        SyncUpdaterService,
        item_to_update=group_updatable_item
    )
