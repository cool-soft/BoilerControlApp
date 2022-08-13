from datetime import timedelta

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory
from updater_keychain.keychain_item import UpdaterKeychainWithDBStorage

from backend.constants import keychain_names
from backend.providers.temp_graph_provider import TempGraphProvider


class TempGraphProviderContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    db_session_provider = Dependency()
    temp_graph_cache_repository = Dependency()
    keychain_repository = Dependency()
    temp_graph_loader = Dependency()

    temp_graph_updater_keychain = Factory(
        UpdaterKeychainWithDBStorage,
        update_interval=timedelta(seconds=3600),  # TODO: this
        keychain_name=keychain_names.TEMP_GRAPH_UPDATE_KEYCHAIN_NAME,
        db_session_factory=db_session_provider,
        keychain_repository=keychain_repository
    )
    temp_graph_provider = Factory(
        TempGraphProvider,
        temp_graph_loader=temp_graph_loader,
        db_session_factory=db_session_provider,
        temp_graph_repository=temp_graph_cache_repository,
        updater_keychain=temp_graph_updater_keychain
    )
