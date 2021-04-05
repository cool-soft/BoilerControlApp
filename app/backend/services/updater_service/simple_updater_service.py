import asyncio
import logging
from typing import List, Optional

import pandas as pd
from dateutil.tz import tzlocal

from backend.services.updater_service.updatable_item.updatable_item import UpdatableItem
from backend.services.updater_service.updater_service import UpdaterService


class SimpleUpdaterService(UpdaterService):

    def __init__(self,
                 items_to_update: Optional[List[UpdatableItem]] = None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        if items_to_update is None:
            items_to_update = []
        self._items_to_update = items_to_update

        self._logger.debug(f"Items to update count {len(items_to_update)}")

    def set_items_to_update(self, items_to_update: List[UpdatableItem]):
        self._logger.debug(f"Items list to update is set; Found {len(items_to_update)} items to update")
        self._items_to_update = items_to_update

    async def run_updater_service_async(self):
        self._logger.debug(f"Service is started")

        while True:
            self._logger.debug("Running updating cycle")
            await self._update_items()
            await self._sleep_to_next_update()

    async def _update_items(self):
        self._logger.debug("Requested items to update unpacked graph")

        for item in self._get_unpacked_dependencies_graph():
            if item.is_need_update():
                self._logger.debug(f"Updating item {item}")
                await item.update_async()

    def _get_unpacked_dependencies_graph(self):
        self._logger.debug("Unpacked dependencies graph is requested")

        unpacked_graph = []
        items_to_process = self._items_to_update.copy()
        while len(items_to_process) > 0:
            item = items_to_process.pop(0)
            for dependency in item.get_dependencies():
                if dependency not in unpacked_graph:
                    items_to_process.append(dependency)
                    break
            else:
                self._logger.debug(f"Unpacked item {item}")
                unpacked_graph.append(item)

        self._logger.debug(f"Found {len(unpacked_graph)} items with dependencies")
        return unpacked_graph

    async def _sleep_to_next_update(self):
        next_update_datetime = self._get_next_update_datetime()
        datetime_now = pd.Timestamp.now(tz=tzlocal())

        timedelta_to_next_update = next_update_datetime - datetime_now
        zero_timedelta = pd.Timedelta(seconds=0)
        timedelta_to_next_update = max(timedelta_to_next_update, zero_timedelta)

        self._logger.debug(f"Sleeping {timedelta_to_next_update}")
        await asyncio.sleep(timedelta_to_next_update.total_seconds())

    def _get_next_update_datetime(self):
        self._logger.debug("Requested next update datetime")

        next_update_datetime = None
        for item in self._get_unpacked_dependencies_graph():
            item_next_update_datetime = item.get_next_update_datetime()
            if next_update_datetime is None:
                next_update_datetime = item_next_update_datetime
            elif item_next_update_datetime is not None:
                next_update_datetime = min(next_update_datetime, item_next_update_datetime)

        self._logger.debug(f"Next update datetime is {next_update_datetime}")
        return next_update_datetime
