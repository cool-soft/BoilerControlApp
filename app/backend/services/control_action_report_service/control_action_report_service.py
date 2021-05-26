from typing import List, Tuple

import pandas as pd
from boiler.constants import column_names

from backend.repositories.control_action_repository import ControlActionsRepository

from .abstract_control_action_report_service import AbstractControlActionReportService
from ...models.api.v3.control_action import ControlAction


class ControlActionReportService(AbstractControlActionReportService):

    def __init__(self,
                 timestamp_report_pattern_v1: str,
                 control_action_repository: ControlActionsRepository
                 ) -> None:
        self._timestamp_report_pattern_v1 = timestamp_report_pattern_v1
        self._control_action_repository = control_action_repository

    async def report_v1(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[Tuple[str, float]]:
        boiler_control_actions_df = \
            await self._control_action_repository.get_control_actions_by_timestamp_range(
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

    async def report_v2(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[Tuple[str, float]]:
        boiler_control_actions_df = \
            await self._control_action_repository.get_control_actions_by_timestamp_range(
                start_timestamp,
                end_timestamp
            )
        predicted_boiler_temp_list = []
        if not boiler_control_actions_df.empty:

            datetime_column = boiler_control_actions_df[column_names.TIMESTAMP]
            datetime_column = datetime_column.dt.tz_convert(report_timezone)
            datetime_column = datetime_column.to_list()

            boiler_out_temps = boiler_control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
            boiler_out_temps = boiler_out_temps.round(1)
            boiler_out_temps = boiler_out_temps.to_list()

            for datetime_, boiler_out_temp in zip(datetime_column, boiler_out_temps):
                predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

        return predicted_boiler_temp_list

    async def report_v3(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[ControlAction]:
        boiler_control_actions_df = \
            await self._control_action_repository.get_control_actions_by_timestamp_range(
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
                    ControlAction(
                        timestamp=datetime_,
                        forward_temp=boiler_out_temp
                    )
                )

        return control_actions_list
