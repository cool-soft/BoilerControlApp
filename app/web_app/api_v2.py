from datetime import datetime
from typing import Optional

from dateutil.tz import gettz
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import config
import consts
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from dependency_injection import get_dependency

app = FastAPI()


@app.get("/getPredictedBoilerT", response_class=JSONResponse)
def get_predicted_boiler_t(
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        response_timezone: Optional[str] = config.BOILER_CONTROL_TIMEZONE
):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    Принимает 3 **опциональных** параметра.
    - **start_datetime**: Дата время начала управляющего воздействия в формате ISO8601 (2020-01-30T00:36:05+05:00).
    - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO8601 (2020-01-30T01:59:59+05:00).
    - **response_timezone**: Имя временной зоны для генерации ответа. По-умолчанию берется из конфигов.
    """

    response_timezone = gettz(response_timezone)
    if start_datetime is None:
        start_datetime = datetime.now(tz=response_timezone)
    if end_datetime is None:
        end_datetime = start_datetime + consts.TIME_TICK
    boiler_t_predictor = get_dependency(BoilerTPredictor)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(start_datetime, end_datetime)

    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(response_timezone)

        boiler_t = row[consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_, boiler_t))

    return predicted_boiler_t_ds
