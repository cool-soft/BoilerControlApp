import asyncio
import logging

import pandas as pd
from dateutil.tz import tzlocal

from boiler.constants import column_names
from boiler.temp_graph.repository.temp_graph_repository import TempGraphRepository
from boiler.temp_requirements.repository.temp_requirements_simple_repository import TempRequirementsSimpleRepository
from boiler.weater_info.repository.weather_repository import WeatherRepository
from backend.services.temp_requirements_update_service.temp_requirements_update_service import \
    TempRequirementsUpdateService


class SimpleTempRequirementsService(TempRequirementsUpdateService):

    def __init__(self,
                 temp_graph_repository: TempGraphRepository = None,
                 weather_repository: WeatherRepository = None,
                 temp_requirements_repository: TempRequirementsSimpleRepository = None,
                 temp_graph_requirements_calculator=None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the provider")

        self._service_lock = asyncio.Lock()

        self._weather_repository = weather_repository
        self._temp_requirements_repository = temp_requirements_repository
        self._temp_graph_repository = temp_graph_repository

        self._temp_requirements_calculator = temp_graph_requirements_calculator

    def set_temp_graph_repository(self, temp_graph_repository):
        self._logger.debug("Temp graph repository is set")
        self._temp_graph_repository = temp_graph_repository

    def set_weather_repository(self, weather_repository: WeatherRepository):
        self._logger.debug("Weather repository is set")
        self._weather_repository = weather_repository

    def set_temp_requirements_repository(self, temp_requirements_repository: TempRequirementsSimpleRepository):
        self._logger.debug("Temp requirements repository is set")
        self._temp_requirements_repository = temp_requirements_repository

    def set_temp_graph_requirements_calculator(self, temp_graph_requirements_calculator):
        self._logger.debug("Temp graph requirements calculator is set")
        self._temp_requirements_calculator = temp_graph_requirements_calculator

    async def update_temp_requirements_async(self):
        self._logger.debug("Requested temp requirements update")
        async with self._service_lock:
            temp_requirements_df = await self._calc_temp_requirements()
            await self._temp_requirements_repository.update_temp_requirements(temp_requirements_df)
            await self._drop_expired_temp_requirements()

    async def _calc_temp_requirements(self):
        self._logger.debug("Calculating temp requirements")

        temp_graph = await self._temp_graph_repository.get_temp_graph()
        self._temp_requirements_calculator.set_temp_graph(temp_graph)

        start_datetime = pd.Timestamp.now(tz=tzlocal())
        weather_df = await self._weather_repository.get_weather_info(start_datetime)
        weather_temp_arr = weather_df[column_names.WEATHER_TEMP].to_numpy()

        temp_requirements_datetime_list = weather_df[column_names.TIMESTAMP].to_list()
        temp_requirements = []
        for weather_temp, datetime_ in zip(weather_temp_arr, temp_requirements_datetime_list):
            required_temp = self._temp_requirements_calculator.get_temp_requirements_for_weather_temp(weather_temp)
            temp_requirements.append({
                column_names.TIMESTAMP: datetime_,
                column_names.FORWARD_PIPE_COOLANT_TEMP: required_temp[column_names.FORWARD_PIPE_COOLANT_TEMP],
                column_names.BACKWARD_PIPE_COOLANT_TEMP: required_temp[column_names.BACKWARD_PIPE_COOLANT_TEMP]
            })
        temp_requirements_df = pd.DataFrame(temp_requirements)

        self._logger.debug("Temp requirements are calculated")
        return temp_requirements_df

    async def _drop_expired_temp_requirements(self):
        datetime_now = pd.Timestamp.now(tz=tzlocal())
        self._logger.debug(f"Droping expiried temp requirements, that older than {datetime_now}")
        await self._temp_requirements_repository.delete_temp_requirements_older_than(datetime_now)
