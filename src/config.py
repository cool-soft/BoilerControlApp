
HOME_T_DISPERSION_COEFFICIENT = 0.97

FORECAST_WEATHER_SERVER_ADDRESS = "https://lysva.agt.town/"
FORECAST_WEATHER_SERVER_TIMEZONE = "Asia/Yekaterinburg"

T_GRAPH_PATH = "../storage/t_graph.csv"
HOMES_DELTAS_PATH = "../storage/homes_time_delta.csv"
OPTIMIZED_T_TABLE_PATH = "../storage/optimized_t_table.pickle"

BOILER_CONTROL_REQUEST_DATETIME_PATTERNS = (
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})",
    r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})"
)
BOILER_CONTROL_RESPONSE_DATETIME_PATTERN = "%Y-%m-%d %H:%M"
BOILER_CONTROL_TIMEZONE = "Asia/Yekaterinburg"

SERVICE_PORT = 270
SERVICE_HOST = "0.0.0.0"
FLASK_DEBUG = True
