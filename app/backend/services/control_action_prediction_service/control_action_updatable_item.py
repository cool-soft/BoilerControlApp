from typing import Optional

from aiorwlock import RWLock

from backend.services.control_action_prediction_service.control_actions_prediction_service \
    import ControlActionPredictionService
from updater.updatable_item.updatable_item import UpdatableItem
from dependency_injector.providers import Provider


class ControlActionUpdatableItem(UpdatableItem):

    def __init__(self,
                 provider: Optional[Provider] = None,
                 dynamic_config_lock: Optional[RWLock] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._provider = provider
        self._dynamic_settings_lock = dynamic_config_lock

        self._logger.debug(f"Service provider is set to {provider}")
        self._logger.debug(f"Dynamic settings lock is set to {dynamic_config_lock}")

    def set_service_provider(self, provider: Provider):
        self._logger.debug(f"Service provider is set to {provider}")
        self._provider = provider

    def set_dynamic_settings_lock(self, lock: RWLock):
        self._logger.debug(f"Dynamic settings lock is set to {lock}")
        self._dynamic_settings_lock = lock

    async def _run_update_async(self):
        self._logger.debug("Run update")
        try:
            async with self._dynamic_settings_lock.reader_lock:
                service: ControlActionPredictionService = self._provider()
            await service.predict_control_actions_async()

        except:
            import traceback
            traceback.print_exc()
            raise

