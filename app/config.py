HOME_T_DISPERSION_COEFFICIENT = 0.97

WEATHER_FORECAST_SERVER_ADDRESS = "https://lysva.agt.town/"
WEATHER_FORECAST_SERVER_TIMEZONE = "Asia/Yekaterinburg"
WEATHER_FORECAST_UPDATE_INTERVAL = 600

T_GRAPH_PATH = "../storage/t_graph.csv"
HOMES_DELTAS_PATH = "../storage/homes_time_delta.csv"
OPTIMIZED_T_TABLE_PATH = "../storage/optimized_t_table.pickle"

LOG_PATH = "../logs/log.log"
LOG_LEVEL = "DEBUG"  # "INFO"
LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"  # " {%(pathname)s:%(lineno)d}"

BOILER_CONTROL_REQUEST_DATETIME_PATTERNS = (
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})",
    r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})"
)
BOILER_CONTROL_RESPONSE_DATETIME_PATTERN = "%Y-%m-%d %H:%M"
BOILER_CONTROL_TIMEZONE = "Asia/Yekaterinburg"

SERVICE_PORT = 270
SERVICE_HOST = "0.0.0.0"
