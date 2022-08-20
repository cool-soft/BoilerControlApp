from datetime import timedelta

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory, Callable
from updater.update_datetime_memento.update_datetime_memento import UpdateDatetimeMementoWithDBRepo
from updater.update_keychain import UpdateKeychain

from backend.constants import keychain_names
from backend.providers.temp_graph_provider import TempGraphProvider


class TempGraphLoaderWithCacheContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    db_session_provider = Dependency()
    temp_graph_cache_repository = Dependency()
    keychain_repository = Dependency()
    temp_graph_loader = Dependency()

    temp_graph_updater_keychain = Factory(
        UpdateKeychain,
        update_interval=Callable(timedelta, seconds=config.update_interval),
        update_datetime_memento=Factory(
            UpdateDatetimeMementoWithDBRepo,
            db_session_factory=db_session_provider,
            memento_name=keychain_names.TEMP_GRAPH_UPDATE_KEYCHAIN_NAME,
            update_datetime_repository=keychain_repository,
        )
    )
    temp_graph_loader_with_cache = Factory(
        TempGraphProvider,
        temp_graph_loader=temp_graph_loader,
        db_session_factory=db_session_provider,
        temp_graph_repository=temp_graph_cache_repository,
        update_keychain=temp_graph_updater_keychain
    )
