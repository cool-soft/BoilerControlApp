from datetime import datetime
from typing import List, Tuple

import pandas as pd
from boiler.constants import column_names

from backend.logging import logger
from backend.models.control_action.control_action_v3 import ControlActionV3
from backend.repositories.control_action_repository import ControlActionsRepository


class ControlActionReportService:

    def __init__(self,
                 timestamp_report_pattern_v1: str,
                 control_action_repository: ControlActionsRepository
                 ) -> None:
        self._timestamp_report_pattern_v1 = timestamp_report_pattern_v1
        self._control_action_repository = control_action_repository

        logger.debug("Creating instance")

    def report_v1(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[Tuple[str, float]]:
        logger.info(
            f"Creating control action report for datetime range {start_timestamp}, {end_timestamp} "
            f"in timezone{report_timezone}"
        )
        boiler_control_actions_df = \
            self._control_action_repository.get_control_actions_by_timestamp_range(
                start_timestamp,
                end_timestamp
            )
        predicted_boiler_temp_list = []
        if not boiler_control_actions_df.empty:

            datetime_column = boiler_control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.dt.strftime(self._timestamp_report_pattern_v1)
            datetime_column = datetime_column.to_list()

            boiler_out_temps = boiler_control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
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
        logger.info(
            f"Creating control action report for datetime range {start_timestamp}, {end_timestamp} "
            f"in timezone{report_timezone}"
        )
        boiler_control_actions_df = \
            self._control_action_repository.get_control_actions_by_timestamp_range(
                start_timestamp,
                end_timestamp
            )
        control_action_list = []
        if not boiler_control_actions_df.empty:

            datetime_column = boiler_control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.dt.to_pydatetime()

            boiler_out_temps = boiler_control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
            boiler_out_temps = boiler_out_temps.round(1)
            boiler_out_temps = boiler_out_temps.to_list()

            for datetime_, boiler_out_temp in zip(datetime_column, boiler_out_temps):
                # noinspection PyTypeChecker
                control_action_list.append((datetime_, boiler_out_temp))

        return control_action_list

    def report_v3(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[ControlActionV3]:
        logger.info(
            f"Creating control action report for datetime range {start_timestamp}, {end_timestamp} "
            f"in timezone{report_timezone}"
        )
        boiler_control_actions_df = \
            self._control_action_repository.get_control_actions_by_timestamp_range(
                start_timestamp,
                end_timestamp
            )
        control_actions_list = []
        if not boiler_control_actions_df.empty:

            datetime_column = boiler_control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.to_list()

            boiler_out_temps = boiler_control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
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
