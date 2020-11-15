
import datetime

TIME_STEP = datetime.timedelta(0, 0, 0, 0, 3)  # 3 minutes

TIMESTAMP_COLUMN_NAME = "dTimeStamp"
BOILER_COLUMN_NAME = "BOILER"
WEATHER_T_COLUMN_NAME = "weather_t"
T_GRAPH_HOME_T_COLUMN_NAME = "home_t"
TIME_DELTA_COLUMN_NAME = "time_delta"
HOME_NAME_COLUMN_NAME = "home_name"

SOFT_M_WEATHER_T_COLUMN_NAME = "temp"

HOME_T_DISPERSION_COEFFICIENT = 0.97

REMOTE_HOST = "https://lysva.agt.town/"
BOILER_ID = 1

PROVIDER_VALUES_CACHE_SIZE = 480

T_GRAPH_PATH = "storage\\t_graph.csv"
HOMES_DELTAS_PATH = "storage\\homes_time_delta.csv"
OPTIMIZED_T_TABLE_PATH = "storage\\optimized_t_table.pickle"
DB_PATH = "storage\\statistic.db"
