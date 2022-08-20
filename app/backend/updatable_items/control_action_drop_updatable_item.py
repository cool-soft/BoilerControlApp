from dependency_injector.providers import Provider
from updater.updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.services.control_action_service import ControlActionService


class ControlActionDropUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self, provider: Provider, **kwargs) -> None:
        super().__init__(**kwargs)

        self._provider = provider

        logger.debug(f"Service provider is set to {provider}")

    def _run_update(self) -> None:
        logger.debug("Run update")
        service: ControlActionService = self._provider()
        service.drop_old_control_action()
