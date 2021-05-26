from dependency_injector.providers import Provider
from updater.updatable_item.simple_updatable_item import SimpleUpdatableItem

from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService


class TempGraphUpdatableItem(SimpleUpdatableItem):

    def __init__(self,
                 provider: Provider,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        self._provider = provider

        self._logger.debug(f"Service provider is set to {provider}")

    async def _run_update_async(self):
        self._logger.debug("Run update")
        service: TempGraphUpdateService = self._provider()
        await service.update_temp_graph_async()
