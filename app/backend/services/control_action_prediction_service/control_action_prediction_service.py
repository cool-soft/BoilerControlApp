import asyncio
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Tuple

import pandas as pd
from boiler.constants import dataset_prototypes
from boiler.control_action.predictors.abstract_control_action_predictor import AbstractControlActionPredictor
from boiler.data_processing.timestamp_round_algorithm import AbstractTimestampRoundAlgorithm
from boiler.heating_system.model_requirements.abstract_model_requirements import AbstractModelRequirements
from dateutil.tz import tzlocal

from backend.repositories.control_action_repository import ControlActionsRepository
from backend.repositories.weather_forecast_repository import WeatherForecastRepository


class ControlActionPredictionService:

    def __init__(self,
                 weather_forecast_repository: WeatherForecastRepository,
                 control_actions_repository: ControlActionsRepository,
                 control_action_predictor: AbstractControlActionPredictor,
                 model_requirements: AbstractModelRequirements,
                 timestamp_round_algo: AbstractTimestampRoundAlgorithm,
                 timedelta: pd.Timedelta,
                 timedelta_predict_forward: pd.Timedelta = pd.Timedelta(seconds=3600),
                 executor: ThreadPoolExecutor = None
                 ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._weather_forecast_repository = weather_forecast_repository
        self._control_action_repository = control_actions_repository
        self._control_action_predictor = control_action_predictor
        self._model_requirements = model_requirements
        self._timestamp_round_algo = timestamp_round_algo
        self._timedelta_predict_forward = timedelta_predict_forward
        self._timedelta = timedelta
        self._executor = executor

    async def update_control_actions_async(self) -> None:
        self._logger.debug("Requested updating control actions")
        control_action_start_timestamp, control_action_end_timestamp = self._calc_control_action_start_end_timestamp()
        control_action_current_timestamp = control_action_start_timestamp
        while control_action_current_timestamp <= control_action_end_timestamp:
            await self._update_control_action_for_timestamp(control_action_current_timestamp)
            control_action_current_timestamp += self._timedelta
        await self._control_action_repository.drop_control_actions_older_than(control_action_start_timestamp)

    def _calc_control_action_start_end_timestamp(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        control_action_start_timestamp = pd.Timestamp.now(tzlocal())
        control_action_start_timestamp = self._timestamp_round_algo.round_value(control_action_start_timestamp)
        control_action_start_timestamp = control_action_start_timestamp
        control_action_end_timestamp = control_action_start_timestamp + self._timedelta_predict_forward
        return control_action_start_timestamp, control_action_end_timestamp

    async def _update_control_action_for_timestamp(self,
                                                   control_action_timestamp: pd.Timestamp
                                                   ) -> None:
        weather_forecast_start_timestamp, weather_forecast_end_timestamp = \
            self._model_requirements.get_weather_start_end_timestamps(control_action_timestamp)
        weather_forecast_df = await self._weather_forecast_repository.get_weather_forecast_by_timestamp_range(
            weather_forecast_start_timestamp,
            weather_forecast_end_timestamp
        )
        system_states_history_df = dataset_prototypes.HEATING_SYSTEM_STATE.copy()
        control_action_df = await self._predict_control_action_in_executor(
            control_action_timestamp,
            system_states_history_df,
            weather_forecast_df
        )
        await self._control_action_repository.add_control_actions(control_action_df)

    async def _predict_control_action_in_executor(self,
                                                  control_action_timestamp: pd.Timestamp,
                                                  system_states_history_df: pd.DataFrame,
                                                  weather_forecast_df: pd.DataFrame
                                                  ) -> pd.DataFrame:
        control_action_df = await asyncio.get_running_loop().run_in_executor(
            self._executor,
            self._control_action_predictor.predict_one,
            weather_forecast_df,
            system_states_history_df,
            control_action_timestamp
        )
        return control_action_df
