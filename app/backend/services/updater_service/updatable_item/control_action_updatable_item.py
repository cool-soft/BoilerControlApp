from backend.services.control_action_prediction_service.control_actions_prediction_service \
    import ControlActionPredictionService
from backend.services.updater_service.updatable_item.updatable_item import UpdatableItem
from dependency_injector.providers import Provider


class ControlActionUpdatableItem(UpdatableItem):

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
        service: ControlActionPredictionService = self._provider()
        await service.predict_control_actions_async()
