
import pandas as pd

import consts
import config


def get_timedelta_by_home_name(home_name, path=config.HOMES_DELTAS_PATH):
    time_deltas = load_homes_time_deltas(path)
    time_delta = time_deltas[time_deltas[consts.HOME_NAME_COLUMN_NAME] == home_name]
    return time_delta


def load_homes_time_deltas(path=config.HOMES_DELTAS_PATH):
    time_deltas = pd.read_csv(path)
    return time_deltas
