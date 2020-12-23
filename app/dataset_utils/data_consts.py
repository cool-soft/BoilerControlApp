from datetime import timedelta as _timedelta

TIME_TICK = _timedelta(minutes=3)

TIMESTAMP_COLUMN_NAME = "timestamp"
UPDATED_TIMESTAMP_COLUMN_NAME = "updated_at"
TIME_DELTA_COLUMN_NAME = "time_delta"
WEATHER_T_COLUMN_NAME = "weather_t"
HOME_NAME_COLUMN_NAME = "home_name"
REQUIRED_T_AT_HOME_IN_COLUMN_NAME = "required_t_at_home_in"
REQUIRED_T_AT_HOME_OUT_COLUMN_NAME = "required_t_at_home_out"
BOILER_NAME_COLUMN_NAME = "BOILER"
BOILER_PIPE_1_COLUMN_NAME = "t1"

SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_IN_COLUMN_NAME = "in_t"
SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_OUT_COLUMN_NAME = "out_t"
SOFT_M_TEMP_GRAPH_WEATHER_COLUMN_NAME = "t"
SOFT_M_TIMESTAMP_COLUMN_NAME = "dTimeStamp"
SOFT_M_WEATHER_T_COLUMN_NAME = "temp"
SOFT_M_TIME_COLUMN_NAME = "time"
SOFT_M_DATE_COLUMN_NAME = "date"

DATETIME_PATTERNS = (
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s(?P<hours>\d{2}):(?P<minutes>\d{2}).{7}",
    r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})"
)
