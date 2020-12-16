
from datetime import datetime
from typing import Optional

from dateutil.tz import gettz
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import config
import consts
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from dataset_utils.preprocess_utils import parse_datetime
from dependency_injection import get_dependency

app = FastAPI()


@app.get("/getPredictedBoilerT", response_class=JSONResponse)
def get_predicted_boiler_t(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    """

    raise ValueError("ЕЕЕ, бой")

    boiler_t_predictor = get_dependency(BoilerTPredictor)
    boiler_control_timezone = gettz(config.BOILER_CONTROL_TIMEZONE)

    default_start_datetime = datetime.now(tz=boiler_control_timezone)
    start_datetime = preprocess_datetime(start_date, default_start_datetime, boiler_control_timezone)

    default_end_datetime = start_datetime + consts.TIME_TICK
    end_datetime = preprocess_datetime(end_date, default_end_datetime, boiler_control_timezone)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(start_datetime, end_datetime)

    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(boiler_control_timezone)
        datetime_as_str = datetime_.strftime(config.BOILER_CONTROL_RESPONSE_DATETIME_PATTERN)

        boiler_t = row[consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

    return predicted_boiler_t_ds


def preprocess_datetime(datetime_as_str, default_value, timezone):
    if datetime_as_str is None:
        datetime_ = default_value
    else:
        datetime_ = parse_datetime(
            datetime_as_str,
            config.BOILER_CONTROL_REQUEST_DATETIME_PATTERNS,
            timezone=timezone
        )
    return datetime_
