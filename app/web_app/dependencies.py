from datetime import datetime
from typing import Optional

from dateutil.tz import gettz

import config
import consts
from dataset_utils.preprocess_utils import parse_datetime


class InputDatesRange:

    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        boiler_control_timezone = gettz(config.BOILER_CONTROL_TIMEZONE)

        if start_date is None:
            self.start_date = datetime.now(tz=boiler_control_timezone)
        else:
            self.start_date = parse_datetime(
                start_date,
                config.BOILER_CONTROL_REQUEST_DATETIME_PATTERNS,
                timezone=boiler_control_timezone
            )

        if end_date is None:
            self.end_date = self.start_date + consts.TIME_TICK
        else:
            self.end_date = parse_datetime(
                end_date,
                config.BOILER_CONTROL_REQUEST_DATETIME_PATTERNS,
                timezone=boiler_control_timezone
            )
