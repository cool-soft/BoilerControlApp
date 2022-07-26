from dependency_injector.providers import Provider
from updater.updatable_item.abstract_sync_updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.services.temp_graph_update_service.simple_temp_graph_update_service import SimpleTempGraphUpdateService


class TempGraphUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self,
                 provider: Provider,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        self._provider = provider

        logger.debug(
            f"Creating instance:"
            f"service provider: {provider}"
        )

    def _run_update(self):
        logger.debug("Run update")
        service: SimpleTempGraphUpdateService = self._provider()
        service.update_temp_graph()
