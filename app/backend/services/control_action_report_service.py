from datetime import datetime
from typing import List, Tuple, Callable

import pandas as pd
from boiler.constants import column_names, circuit_types

from backend.models.api import ControlActionV3
from backend.repositories.control_action_repository import ControlActionRepository


class ControlActionReportService:

    def __init__(self,
                 db_session_factory: Callable,
                 control_action_repository: ControlActionRepository,
                 timestamp_report_pattern_v1: str
                 ) -> None:
        self._db_session_factory = db_session_factory
        self._control_action_repository = control_action_repository
        self._timestamp_report_pattern_v1 = timestamp_report_pattern_v1

    def report_v1(self,
                  start_timestamp: pd.Timestamp,
                  end_timestamp: pd.Timestamp,
                  report_timezone
                  ) -> List[Tuple[str, float]]:
        with self._db_session_factory():
            control_actions_df = \
                self._control_action_repository.get_control_action_by_timestamp_range(
                    start_timestamp,
                    end_timestamp,
                    circuit_types.HEATING
                )
        predicted_boiler_temp_list = []
        if not control_actions_df.empty:

            datetime_column = control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.dt.strftime(self._timestamp_report_pattern_v1)
            datetime_column = datetime_column.to_list()

            boiler_out_temps = control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
            boiler_out_temps = boiler_out_temps.round(1)
            boiler_out_temps = boiler_out_temps.to_list()

            for datetime_, boiler_out_temp in zip(datetime_column, boiler_out_temps):
                predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

        return predicted_boiler_temp_list

    def report_v2(self,
                  start_timestamp: pd.Timestamp,
                  end_timestamp: pd.Timestamp,
                  report_timezone
                  ) -> List[Tuple[datetime, float]]:
        with self._db_session_factory():
            control_actions_df = \
                self._control_action_repository.get_control_action_by_timestamp_range(
                    start_timestamp,
                    end_timestamp,
                    circuit_types.HEATING
                )
        control_action_list = []
        if not control_actions_df.empty:

            datetime_column = control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.dt.to_pydatetime()

            boiler_out_temps = control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
            boiler_out_temps = boiler_out_temps.round(1)
            boiler_out_temps = boiler_out_temps.to_list()

            for datetime_, boiler_out_temp in zip(datetime_column, boiler_out_temps):
                control_action_list.append((datetime_, boiler_out_temp))

        return control_action_list

    def report_v3(self,
                  start_timestamp: pd.Timestamp,
                  end_timestamp: pd.Timestamp,
                  report_timezone
                  ) -> List[ControlActionV3]:
        with self._db_session_factory():
            control_actions_df = \
                self._control_action_repository.get_control_action_by_timestamp_range(
                    start_timestamp,
                    end_timestamp,
                    circuit_types.HEATING
                )

        control_actions_list = []
        if not control_actions_df.empty:

            datetime_column = control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.to_list()

            boiler_out_temps = control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
            boiler_out_temps = boiler_out_temps.round(1)
            boiler_out_temps = boiler_out_temps.to_list()

            for datetime_, boiler_out_temp in zip(datetime_column, boiler_out_temps):
                control_actions_list.append(
                    ControlActionV3(
                        timestamp=datetime_,
                        forward_temp=boiler_out_temp
                    )
                )

        return control_actions_list
