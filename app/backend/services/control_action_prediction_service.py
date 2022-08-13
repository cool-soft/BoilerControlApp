from datetime import timedelta
from typing import Tuple

import pandas as pd
from boiler.control_action.predictors.abstract_control_action_predictor import AbstractControlActionPredictor
from boiler.data_processing.timestamp_round_algorithm import AbstractTimestampRoundAlgorithm
from boiler.heating_system.model_requirements.abstract_model_requirements import AbstractModelRequirements
from dateutil import tz
from sqlalchemy.orm import scoped_session

from backend.providers.temp_requirements_provider import TempRequirementsProvider
from backend.repositories.control_action_repository import ControlActionRepository


class ControlActionPredictionService:

    def __init__(self,
                 model_requirements: AbstractModelRequirements,
                 temp_requirements_provider: TempRequirementsProvider,
                 control_action_predictor: AbstractControlActionPredictor,
                 db_session_factory: scoped_session,
                 control_action_repository: ControlActionRepository,
                 timestamp_round_algo: AbstractTimestampRoundAlgorithm,
                 time_tick: pd.Timedelta,
                 timedelta_predict_forward: timedelta = timedelta(seconds=3600),
                 ) -> None:
        self._model_requirements = model_requirements
        self._temp_requirements_provider = temp_requirements_provider
        self._control_action_predictor = control_action_predictor
        self._session_factory = db_session_factory
        self._control_action_repository = control_action_repository
        self._timestamp_round_algo = timestamp_round_algo
        self._time_tick = time_tick
        self._timedelta_predict_forward = timedelta_predict_forward

    def update_control_actions(self) -> None:
        control_action_start_timestamp = pd.Timestamp.now(tz=tz.UTC)
        control_action_start_timestamp = self._timestamp_round_algo.round_value(control_action_start_timestamp)
        control_action_end_timestamp = control_action_start_timestamp + self._timedelta_predict_forward

        requirements_start_timestamp, requirements_end_timestamp = self._calc_temp_requirements_start_end_timestamp(
            control_action_start_timestamp,
            control_action_end_timestamp
        )
        temp_requirements_df = self._temp_requirements_provider.get_temp_requirements(
            requirements_start_timestamp, requirements_end_timestamp
        )

        control_action_df = self._calc_control_action(
            control_action_start_timestamp,
            control_action_end_timestamp,
            temp_requirements_df
        )
        with self._session_factory() as session:
            self._control_action_repository.add_control_action(control_action_df)
            session.commit()
        self._session_factory.remove()

    def _calc_temp_requirements_start_end_timestamp(self,
                                                    control_action_start_timestamp: pd.Timestamp,
                                                    control_action_end_timestamp: pd.Timestamp
                                                    ) -> Tuple[pd.Timestamp, pd.Timestamp]:
        requirements_start_timestamp, _ = \
            self._model_requirements.get_weather_start_end_timestamps(control_action_start_timestamp)
        _, weather_forecast_end_timestamp = \
            self._model_requirements.get_weather_start_end_timestamps(control_action_end_timestamp)
        return requirements_start_timestamp, weather_forecast_end_timestamp + self._time_tick

    def _calc_control_action(self, control_action_start_timestamp, control_action_end_timestamp, temp_requirements_df):
        control_actions_list = []
        control_action_timestamp = control_action_start_timestamp
        while control_action_timestamp <= control_action_end_timestamp:
            control_action_df = self._control_action_predictor.predict_one(
                temp_requirements_df,
                control_action_timestamp
            )
            control_actions_list.append(control_action_df)
            control_action_timestamp += self._time_tick
        control_action_df = pd.concat(control_actions_list)
        return control_action_df
