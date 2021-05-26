from typing import List, Tuple

import pandas as pd


class AbstractControlActionReportService:

    def report_v1(self,
                  start_timestamp: pd.Timestamp,
                  end_timestamp: pd.Timestamp,
                  report_timezone
                  ) -> List[Tuple[str, float]]:
        raise NotImplementedError
