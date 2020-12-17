from datetime import datetime
from typing import Optional

from dateutil.tz import gettz
from fastapi import APIRouter
from fastapi.responses import JSONResponse

import config
import consts
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from dependency_injection import get_dependency

api_router = APIRouter(prefix="/api/v2")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse)
def get_predicted_boiler_t(
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        timezone_name: Optional[str] = config.BOILER_CONTROL_TIMEZONE
):
    # noinspection SpellCheckingInspection
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия.
        - **end_datetime**: Дата время окончания управляющего воздействия.
        - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
        По-умолчанию берется из конфигов.

        ---
        Формат времени в запросе:
        - YYYY-MM-DD*HH:MM[:SS[.fffffff]][+HH:MM] где * - 1 любой символ

        Примеры:
        - 2020-01-30 00:17+05:00 - Временная зона для парсинга берется из самой строки, предпочтительный вариант.
        - 2020-01-30 00:17 - Временная зона берется из параметра timezone_name.
        - 2020-01-30T00:17:01.1234567+05:00 - Временная зона для парсинга берется из самой строки, формат «O» в C#.

        ---
        Формат времени в ответе:
        - 2020-01-30T00:17:07+05:00 - Парсится при помощи DateTimeStyle.RoundtripKind в C#.
        Временна зона при формировании ответа берётся из парметра timezone_name.

        ---
        Формат timezone_name:
        См. столбец «TZ database name»
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
        """

    boiler_control_timezone = gettz(timezone_name)

    if start_datetime is None:
        start_datetime = datetime.now(tz=boiler_control_timezone)
    if start_datetime.tzname() is None:
        start_datetime = start_datetime.astimezone(boiler_control_timezone)

    if end_datetime is None:
        end_datetime = start_datetime + consts.TIME_TICK
    if end_datetime.tzname() is None:
        end_datetime = end_datetime.astimezone(boiler_control_timezone)

    boiler_t_predictor = get_dependency(BoilerTPredictor)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(start_datetime, end_datetime)

    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(boiler_control_timezone)

        boiler_t = row[consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_, boiler_t))

    return predicted_boiler_t_ds
