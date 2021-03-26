from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.tz import gettz
from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException
from starlette import status

from backend.containers.core import Core
from boiler.constants import time_tick
from boiler.parsing_utils.datetime_parsing import parse_datetime


class InputTimezone:

    @inject
    def __init__(
            self,
            timezone_name: Optional[str] = None,
            datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
    ):
        if timezone_name is None:
            timezone_name = datetime_processing_params.get("default_timezone")

        timezone = gettz(timezone_name)
        if timezone is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"incorrect timezone_name \"{timezone_name}\"",
            )

        self.timezone = timezone
        self.name = timezone_name


class InputDatesRange:

    @inject
    def __init__(
            self,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            work_timezone: InputTimezone = Depends(),
            datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
    ):
        request_datetime_patterns = datetime_processing_params.get("request_patterns")

        if start_date is None:
            start_date = pd.Timestamp.now(tz=work_timezone.timezone)
        else:
            start_date = pd.Timestamp(
                parse_datetime(start_date, request_datetime_patterns, timezone=work_timezone.timezone)
            )

        if end_date is None:
            end_date = start_date + time_tick.TIME_TICK
        else:
            end_date = pd.Timestamp(
                parse_datetime(end_date, request_datetime_patterns, timezone=work_timezone.timezone)
            )

        if start_date <= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be less than end_date"
            )

        self.start_date = start_date
        self.end_date = end_date


class InputDatetimeRange:

    @inject
    def __init__(
            self,
            start_datetime: Optional[datetime] = None,
            end_datetime: Optional[datetime] = None,
            work_timezone: InputTimezone = Depends(),
    ):
        if start_datetime is None:
            start_datetime = pd.Timestamp.now(tz=work_timezone.timezone)
        else:
            start_datetime = pd.Timestamp(start_datetime)
        if start_datetime.tz is None:
            start_datetime = start_datetime.tz_localize(tz=work_timezone.timezone)

        if end_datetime is None:
            end_datetime = start_datetime + time_tick.TIME_TICK
        else:
            end_datetime = pd.Timestamp(end_datetime)
        if end_datetime.tz is None:
            end_datetime = end_datetime.tz_localize(tz=work_timezone.timezone)

        if start_datetime <= end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_datetime must be less than end_datetime"
            )

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
