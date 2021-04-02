import asyncio
import logging

import pandas as pd
from dateutil.tz import tzlocal

from boiler.constants import column_names
from boiler.weater_info.repository.async_weather_repository import AsyncWeatherRepository
from backend.repositories.async_temp_requirements_repository import AsyncTempRequirementsRepository
from backend.services.temp_graph_service.temp_graph_service import TempGraphService
from backend.services.temp_requirements_service.temp_requirements_service import TempRequirementsService


class SimpleTempRequirementsService(TempRequirementsService):

    def __init__(self,
                 temp_graph_service: TempGraphService = None,
                 weather_repository: AsyncWeatherRepository = None,
                 temp_requirements_repository: AsyncTempRequirementsRepository = None,
                 temp_graph_requirements_calculator=None,
                 update_interval=600):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._service_lock = asyncio.Lock()
        self._temp_requirements_update_interval = update_interval
        self._temp_requirements_last_update = None

        self._weather_repository = weather_repository
        self._temp_requirements_repository = temp_requirements_repository

        self._temp_graph_service = temp_graph_service

        self._temp_graph_requirements_calculator = temp_graph_requirements_calculator

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Temp requirements update interval is set to {update_interval}")
        self._temp_requirements_update_interval = update_interval

    def set_temp_graph_service(self, temp_graph_service):
        self._logger.debug("Temp graph service is set")
        self._temp_graph_service = temp_graph_service

    def set_weather_repository(self, weather_repository: AsyncWeatherRepository):
        self._logger.debug("Weather repository is set")
        self._weather_repository = weather_repository

    def set_temp_requirements_repository(self, temp_requirements_repository: AsyncTempRequirementsRepository):
        self._logger.debug("Temp requirements repository is set")
        self._temp_requirements_repository = temp_requirements_repository

    def set_temp_graph_requirements_calculator(self, temp_graph_requirements_calculator):
        self._logger.debug("Temp graph requirements calculator is set")
        self._temp_graph_requirements_calculator = temp_graph_requirements_calculator

    async def update_temp_requirements(self, start_datetime: pd.Timestamp = None, end_datetime: pd.Timestamp = None):
        self._logger.debug(f"Requested temp requirements update from {start_datetime} to {end_datetime}")

        async with self._service_lock:
            max_cached_datetime = await self._temp_requirements_repository.get_max_timestamp()

            if max_cached_datetime is None or self._is_cached_requirements_expired():
                await self._calc_temp_requirements(start_datetime, end_datetime)

            elif max_cached_datetime < end_datetime:
                start_datetime = max_cached_datetime
                await self._calc_temp_requirements(start_datetime, end_datetime)

            await self._drop_expired_temp_requirements()

    async def _calc_temp_requirements(self, start_datetime, end_datetime):
        temp_graph = await self._temp_graph_service.get_temp_graph()
        self._temp_graph_requirements_calculator.set_temp_graph(temp_graph)

        weather_df = await self._weather_repository.get_weather_info(start_datetime, end_datetime)
        weather_temp_arr = weather_df[column_names.WEATHER_TEMP].to_numpy()

        temp_requirements_datetime_list = weather_df[column_names.TIMESTAMP].to_list()
        temp_requirements = []
        for weather_temp, datetime_ in zip(weather_temp_arr, temp_requirements_datetime_list):
            required_temp = self._temp_graph_requirements_calculator.\
                get_temp_requirements_for_weather_temp(weather_temp)
            temp_requirements.append({
                column_names.TIMESTAMP: datetime_,
                column_names.FORWARD_PIPE_COOLANT_TEMP: required_temp[column_names.FORWARD_PIPE_COOLANT_TEMP],
                column_names.BACKWARD_PIPE_COOLANT_TEMP: required_temp[column_names.BACKWARD_PIPE_COOLANT_TEMP]
            })
        temp_requirements_df = pd.DataFrame(temp_requirements)

        await self._temp_requirements_repository.update_temp_requirements(temp_requirements_df)
        self._temp_requirements_last_update = pd.Timestamp.now(tz=tzlocal())

    def _is_cached_requirements_expired(self):
        self._logger.debug("Checking that cached temp requirements is not expired")

        if self._temp_requirements_last_update is None:
            self._logger.debug("Temp requirements is never updated")
            return True

        datetime_now = pd.Timestamp.now(tz=tzlocal())
        requirements_lifetime = (datetime_now - self._temp_requirements_last_update)
        if requirements_lifetime.total_seconds() > self._temp_requirements_update_interval:
            self._logger.debug("Temp requirements are expired")
            return True

        self._logger.debug("Temp requirements are not expired")
        return False

    async def _drop_expired_temp_requirements(self):
        datetime_now = pd.Timestamp.now(tz=tzlocal())
        await self._temp_requirements_repository.delete_temp_requirements_older_than(datetime_now)
