import pandas as pd
from typing import Optional

from dateutil.tz import gettz
from dependency_injector.wiring import inject, Provide
from fastapi import Depends

from constants import time_tick
from containers.core import Core
from parsing_utils.datetime_parsing import parse_datetime


class InputDatesRange:

    @inject
    def __init__(
            self,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            timezone_name: Optional[str] = None,
            datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
    ):
        if timezone_name is None:
            timezone_name = datetime_processing_params.get("default_timezone")

        work_timezone = gettz(timezone_name)
        request_datetime_patterns = datetime_processing_params.get("request_patterns")

        if start_date is None:
            self.start_date = pd.Timestamp.now(tz=work_timezone)
        else:
            self.start_date = pd.Timestamp(
                parse_datetime(start_date, request_datetime_patterns, timezone=work_timezone)
            )

        if end_date is None:
            self.end_date = self.start_date + time_tick.TIME_TICK
        else:
            self.end_date = pd.Timestamp(
                parse_datetime(end_date, request_datetime_patterns, timezone=work_timezone)
            )
