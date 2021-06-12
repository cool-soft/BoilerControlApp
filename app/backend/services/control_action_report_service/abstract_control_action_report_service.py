from typing import List, Tuple

import pandas as pd

from backend.models.control_action.control_action_v3 import ControlActionV3


class AbstractControlActionReportService:

    async def report_v1(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[Tuple[str, float]]:
        raise NotImplementedError

    async def report_v2(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[Tuple[str, float]]:
        raise NotImplementedError

    async def report_v3(self,
                        start_timestamp: pd.Timestamp,
                        end_timestamp: pd.Timestamp,
                        report_timezone
                        ) -> List[ControlActionV3]:
        raise NotImplementedError
