from dependency_injector.providers import Provider

from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService
from updater.updatable_item.updatable_item import UpdatableItem


class TempGraphUpdatableItem(UpdatableItem):

    def __init__(self,
                 provider: Provider = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._provider = provider

    def set_service_provider(self, provider: Provider):
        self._logger.debug("Service provider is set")
        self._provider = provider

    async def _run_update_async(self):
        self._logger.debug("Running update")
        service: TempGraphUpdateService = self._provider()
        await service.update_temp_graph_async()
