from dependency_injector.providers import Provider
from updater.updatable_item.abstract_sync_updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.providers.temp_graph_provider import TempGraphUpdateService


class TempGraphUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self, provider: Provider, **kwargs) -> None:

        super().__init__(**kwargs)

        self._provider = provider

        logger.debug(
            f"Creating instance:"
            f"service provider: {provider}"
        )

    def _run_update(self):
        logger.debug("Run update")
        service: TempGraphUpdateService = self._provider()
        service.update_temp_graph()
