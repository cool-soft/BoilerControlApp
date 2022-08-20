from datetime import timedelta, datetime, timezone
from typing import Union
import traceback

from requests.exceptions import RequestException
from dependency_injector.providers import Provider
from updater.updatable_item import AbstractSyncUpdatableItem

from backend.logging import logger
from backend.services.control_action_prediction_service import ControlActionPredictionService


class ControlActionUpdatableItem(AbstractSyncUpdatableItem):

    def __init__(self, provider: Provider, retry_interval: timedelta = timedelta(minutes=5), **kwargs) -> None:
        super().__init__(**kwargs)

        self._provider = provider
        self._retry_interval = retry_interval
        self._next_retry_datetime = None

        logger.debug(f"Service provider is set to {provider}")

    def _run_update(self) -> None:
        logger.debug("Run update")
        service: ControlActionPredictionService = self._provider()
        try:
            service.update_control_actions()
        except RequestException:
            traceback.print_exc()
            self._next_retry_datetime = datetime.now(tz=timezone.utc) + self._retry_interval
        else:
            self._next_retry_datetime = None

    def get_next_update_datetime(self) -> Union[datetime, None]:
        next_update_datetime = self._next_retry_datetime
        if next_update_datetime is None:
            next_update_datetime = super(ControlActionUpdatableItem, self).get_next_update_datetime()
        return next_update_datetime
