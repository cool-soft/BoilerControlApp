import asyncio
import logging
from typing import Optional

import pandas as pd
from dateutil.tz import tzlocal

from boiler.constants import column_names
from boiler.weather.interpolators.weather_data_linear_interpolator import WeatherDataLinearInterpolator
from boiler.temp_graph.io.sync.sync_temp_graph_loader import SyncTempGraphLoader
from boiler.temp_requirements.repository.db.async_.temp_requirements_db_async_repository \
    import TempRequirementsDBAsyncRepository
from boiler.weather.io.async_.async_weather_loader import AsyncWeatherLoader
from backend.services.temp_requirements_update_service.temp_requirements_update_service import \
    TempRequirementsUpdateService


class SimpleTempRequirementsService(TempRequirementsUpdateService):

    def __init__(self,
                 temp_graph_loader: Optional[SyncTempGraphLoader] = None,
                 weather_loader: Optional[AsyncWeatherLoader] = None,
                 temp_requirements_repository: Optional[TempRequirementsDBAsyncRepository] = None,
                 temp_graph_requirements_calculator=None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the provider")

        self._service_lock = asyncio.Lock()

        self._weather_loader = weather_loader
        self._temp_requirements_repository = temp_requirements_repository
        self._temp_graph_loader = temp_graph_loader

        self._temp_requirements_calculator = temp_graph_requirements_calculator

    def set_temp_graph_loader(self, temp_graph_loader):
        self._logger.debug("Temp graph repository is set")
        self._temp_graph_loader = temp_graph_loader

    def set_weather_loader(self, weather_loader: AsyncWeatherLoader):
        self._logger.debug("Weather repository is set")
        self._weather_loader = weather_loader

    def set_temp_requirements_repository(self, temp_requirements_repository: TempRequirementsDBAsyncRepository):
        self._logger.debug("Temp requirements repository is set")
        self._temp_requirements_repository = temp_requirements_repository

    def set_temp_graph_requirements_calculator(self, temp_graph_requirements_calculator):
        self._logger.debug("Temp graph requirements calculator is set")
        self._temp_requirements_calculator = temp_graph_requirements_calculator

    async def update_temp_requirements_async(self):
        self._logger.debug("Requested temp requirements update")
        async with self._service_lock:
            weather_df = await self._get_weather_forecast()
            temp_graph = self._get_temp_graph()
            temp_requirements_df = await self._calc_temp_requirements_in_executor(weather_df, temp_graph)
            await self._temp_requirements_repository.update_temp_requirements(temp_requirements_df)
            await self._drop_expired_temp_requirements()

    async def _get_weather_forecast(self):
        start_datetime = pd.Timestamp.now(tz=tzlocal())
        weather_df = await self._weather_loader.load_weather(start_datetime=start_datetime)
        interpolator = WeatherDataLinearInterpolator()
        weather_df = interpolator.interpolate_weather_data(weather_df)
        return weather_df

    def _get_temp_graph(self) -> pd.DataFrame:
        temp_graph_df = self._temp_graph_loader.load_temp_graph()
        return temp_graph_df

    async def _calc_temp_requirements_in_executor(self, weather_df, temp_graph):
        loop = asyncio.get_running_loop()
        temp_requirements = await loop.run_in_executor(
            None,
            self._calc_temp_requirements,
            weather_df,
            temp_graph
        )
        return temp_requirements

    def _calc_temp_requirements(self, weather_df, temp_graph):
        self._logger.debug("Calculating temp requirements")

        self._temp_requirements_calculator.set_temp_graph(temp_graph)

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
        self._logger.debug(f"Dropping expired temp requirements, that older than {datetime_now}")
        await self._temp_requirements_repository.delete_temp_requirements_older_than(datetime_now)
