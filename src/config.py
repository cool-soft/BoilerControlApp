
HOME_T_DISPERSION_COEFFICIENT = 0.97

REMOTE_HOST = "https://lysva.agt.town/"
BOILER_ID = 1

T_GRAPH_PATH = "storage\\t_graph.csv"
HOMES_DELTAS_PATH = "storage\\homes_time_delta.csv"
OPTIMIZED_T_TABLE_PATH = "storage\\optimized_t_table.pickle"

DATETIME_REQUESTS_PATTERNS = (
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})",
    r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\s(?P<hours>\d{1,2}):(?P<minutes>\d{2})"
)

DATETIME_RESPONSE_PATTERN = "%Y-%m-%d %H:%M:%S"

HTTP_PORT = 3000
FLASK_DEBUG = True