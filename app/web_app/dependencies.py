from datetime import datetime
from typing import Optional

from app_configs import GlobalAppConfig
from dateutil.tz import gettz

from dataset_utils import data_consts
from dataset_utils.preprocess_utils import parse_datetime

app_config = GlobalAppConfig()


class InputDatesRange:

    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        boiler_control_timezone = gettz(app_config.datetime_processing.boiler_controller_timezone)

        if start_date is None:
            self.start_date = datetime.now(tz=boiler_control_timezone)
        else:
            self.start_date = parse_datetime(
                start_date,
                app_config.datetime_processing.request_patterns,
                timezone=boiler_control_timezone
            )

        if end_date is None:
            self.end_date = self.start_date + data_consts.TIME_TICK
        else:
            self.end_date = parse_datetime(
                end_date,
                app_config.datetime_processing.request_patterns,
                timezone=boiler_control_timezone
            )
