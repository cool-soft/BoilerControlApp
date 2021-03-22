from datetime import datetime

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


class InputDatetimeRange:

    @inject
    def __init__(
            self,
            start_datetime: Optional[datetime] = None,
            end_datetime: Optional[datetime] = None,
            timezone_name: Optional[str] = None,
            datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
    ):
        if timezone_name is None:
            timezone_name = datetime_processing_params.get("default_timezone")
        work_timezone = gettz(timezone_name)

        if start_datetime is None:
            start_datetime = pd.Timestamp.now(tz=work_timezone)
        else:
            start_datetime = pd.Timestamp(start_datetime)
        if start_datetime.tz is None:
            start_datetime = start_datetime.tz_localize(tz=work_timezone)
        self.start_datetime = start_datetime

        if end_datetime is None:
            end_datetime = start_datetime + time_tick.TIME_TICK
        else:
            end_datetime = pd.Timestamp(end_datetime)
        if end_datetime.tz is None:
            end_datetime = end_datetime.tz_localize(tz=work_timezone)
        self.end_datetime = end_datetime
