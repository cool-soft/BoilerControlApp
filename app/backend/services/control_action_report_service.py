from datetime import datetime, timezone, tzinfo
from typing import List

from boiler.constants import column_names, circuit_types
from sqlalchemy.orm import scoped_session

from backend.models.api import ControlActionAPIModel
from backend.repositories.control_action_repository import ControlActionRepository


class ControlActionReportService:

    def __init__(self,
                 db_session_provider: scoped_session,
                 control_action_repository: ControlActionRepository,
                 ) -> None:
        self._db_session_provider = db_session_provider
        self._control_action_repository = control_action_repository

    def report(self,
               start_timestamp: datetime,
               end_timestamp: datetime,
               response_timezone: tzinfo = timezone.utc,
               circuit_type: str = circuit_types.HEATING
               ) -> List[ControlActionAPIModel]:
        with self._db_session_provider():
            control_actions_df = \
                self._control_action_repository.get_control_action(start_timestamp, end_timestamp, circuit_type)

        control_actions_list = []
        if not control_actions_df.empty:
            control_actions_df[column_names.TIMESTAMP] = \
                control_actions_df[column_names.TIMESTAMP].dt.tz_convert(response_timezone)
            control_actions_df[column_names.FORWARD_TEMP] = control_actions_df[column_names.FORWARD_TEMP].round(1)

            for _, row in control_actions_df.iterrows():
                control_actions_list.append(
                    ControlActionAPIModel(
                        timestamp=row[column_names.TIMESTAMP],
                        circuit_type=row[column_names.CIRCUIT_TYPE],
                        forward_temp=row[column_names.FORWARD_TEMP]
                    )
                )

        self._db_session_provider.remove()
        return control_actions_list
