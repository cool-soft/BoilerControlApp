from datetime import datetime
from typing import Optional

from dateutil.tz import gettz

from dataset_utils import data_consts
from dataset_utils.preprocess_utils import parse_datetime


class InputDatesRange:

    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        boiler_control_timezone = gettz("Asia/Yekaterinburg")

        if start_date is None:
            self.start_date = datetime.now(tz=boiler_control_timezone)
        else:
            self.start_date = parse_datetime(
                start_date,
                (
                    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})',
                    r'(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})'
                ),
                timezone=boiler_control_timezone
            )

        if end_date is None:
            self.end_date = self.start_date + data_consts.TIME_TICK
        else:
            self.end_date = parse_datetime(
                end_date,
                (
                    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})',
                    r'(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})'
                ),
                timezone=boiler_control_timezone
            )
