from dependency_injector.providers import Provider
from updater.updatable_item.abstract_sync_updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.services.control_action_prediction_service \
    import ControlActionPredictionService


class ControlActionUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self,
                 provider: Provider,
                 **kwargs
                 ) -> None:
        super().__init__(**kwargs)

        self._provider = provider

        logger.debug(f"Service provider is set to {provider}")

    def _run_update(self) -> None:
        logger.debug("Run update")
        service: ControlActionPredictionService = self._provider()
        service.update_control_actions()
