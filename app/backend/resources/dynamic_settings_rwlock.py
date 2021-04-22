import logging

from aiorwlock import RWLock
from dependency_injector import resources


class DynamicSettingsRWLock(resources.AsyncResource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    async def init(self) -> RWLock:
        self._logger.debug(f"Initialize aiorwlock")
        lock = RWLock()
        return lock

    async def shutdown(self, lock: RWLock) -> None:
        pass
