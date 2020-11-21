
import datetime

TIME_TICK = datetime.timedelta(minutes=3)

TIMESTAMP_COLUMN_NAME = "dTimeStamp"
WEATHER_T_COLUMN_NAME = "weather_t"
TIME_DELTA_COLUMN_NAME = "time_delta"
HOME_NAME_COLUMN_NAME = "home_name"
REQUIRED_T_IN_HOME_COLUMN_NAME = "required_t_in_home"
BOILER_NAME_COLUMN_NAME = "BOILER"
FORWARD_PIPE_COLUMN_NAME = "t1"

SOFT_M_WEATHER_T_COLUMN_NAME = "temp"
SOFT_M_TIME_COLUMN_NAME = "time"
SOFT_M_DATE_COLUMN_NAME = "date"

DATETIME_PATTERNS = (
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s(?P<hours>\d{2}):(?P<minutes>\d{2}).{7}",
    r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})"
)
