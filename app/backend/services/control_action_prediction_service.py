from typing import Tuple

import pandas as pd
from boiler.constants import dataset_prototypes
from boiler.control_action.predictors.abstract_control_action_predictor import AbstractControlActionPredictor
from boiler.data_processing.timestamp_round_algorithm import AbstractTimestampRoundAlgorithm
from boiler.heating_system.model_requirements.abstract_model_requirements import AbstractModelRequirements
from dateutil.tz import UTC

from backend.logging import logger
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
                 ) -> None:
        logger.debug("Creating instance")
        self._weather_forecast_repository = weather_forecast_repository
        self._control_action_repository = control_actions_repository
        self._control_action_predictor = control_action_predictor
        self._model_requirements = model_requirements
        self._timestamp_round_algo = timestamp_round_algo
        self._timedelta_predict_forward = timedelta_predict_forward
        self._timedelta = timedelta

    def update_control_actions(self) -> None:
        logger.info("Requesting control actions update")
        control_action_start_timestamp, control_action_end_timestamp = self._calc_control_action_start_end_timestamp()
        control_action_current_timestamp = control_action_start_timestamp
        while control_action_current_timestamp <= control_action_end_timestamp:
            self._update_control_action_for_timestamp(control_action_current_timestamp)
            control_action_current_timestamp += self._timedelta
        self._control_action_repository.drop_control_actions_older_than(control_action_start_timestamp)

    def _calc_control_action_start_end_timestamp(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        control_action_start_timestamp = pd.Timestamp.now(UTC)
        control_action_start_timestamp = self._timestamp_round_algo.round_value(control_action_start_timestamp)
        control_action_start_timestamp = control_action_start_timestamp
        control_action_end_timestamp = control_action_start_timestamp + self._timedelta_predict_forward
        return control_action_start_timestamp, control_action_end_timestamp

    def _update_control_action_for_timestamp(self,
                                             control_action_timestamp: pd.Timestamp
                                             ) -> None:
        weather_forecast_start_timestamp, weather_forecast_end_timestamp = \
            self._model_requirements.get_weather_start_end_timestamps(control_action_timestamp)
        weather_forecast_df = self._weather_forecast_repository.get_weather_forecast_by_timestamp_range(
            weather_forecast_start_timestamp,
            weather_forecast_end_timestamp
        )
        system_states_history_df = dataset_prototypes.HEATING_SYSTEM_STATE.copy()
        control_action_df = self._control_action_predictor.predict_one(
            weather_forecast_df,
            system_states_history_df,
            control_action_timestamp
        )
        self._control_action_repository.add_control_actions(control_action_df)
