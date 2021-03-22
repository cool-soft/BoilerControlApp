import logging
from datetime import datetime
from typing import Optional

from dateutil.tz import gettz
import pandas as pd
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from constants import column_names
from containers.core import Core
from containers.services import Services
from constants import time_tick
from services.boiler_temp_prediction_service.boiler_temp_prediction_service \
    import BoilerTempPredictionService

api_router = APIRouter(prefix="/api/v2")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse)
@inject
def get_predicted_boiler_t(
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        timezone_name: Optional[str] = None,
        datetime_processing_params=Depends(Provide[Core.config.datetime_processing]),
        boiler_t_predictor: BoilerTempPredictionService = Depends(
            Provide[Services.boiler_temp_prediction.boiler_temp_prediction_service]
        )
):
    # noinspection SpellCheckingInspection
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия в формате ISO 8601
        См. https://en.wikipedia.org/wiki/ISO_8601.
        - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO 8601.
        - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
        По-умолчанию берется из конфигов.
        См. столбец «TZ database name» https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

        ---
        Формат времени в запросе:
        - YYYY-MM-DD?HH:MM[:SS[.fffffff]][+HH:MM] где ? это T или символ пробела.

        Примеры:
        - 2020-01-30 00:17:07+05:00 - Временная зона для парсинга берется из самой строки, предпочтительный вариант.
        - 2020-01-30 00:17+05 - Временная зона для парсинга берется из самой строки.
        - 2020-01-30 00:17+05:30 - Временная зона для парсинга берется из самой строки.
        - 2020-01-30 00:17 - Временная зона берется из параметра timezone_name.
        - 2020-01-30T00:17:01.1234567+05:00 - Временная зона для парсинга берется из самой строки, формат «O» в C#.

        ---
        Формат времени в ответе:
        - 2020-01-30T00:17:07+05:00 - Парсится при помощи DateTimeStyle.RoundtripKind в C#.
        Временна зона при формировании ответа берётся из парметра timezone_name. По-умолчанию берется из конфигов.
        """

    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler t for dates range "
                  f"from {start_datetime} to {end_datetime} "
                  f"with timezone_name {timezone_name}")

    if timezone_name is None:
        timezone_name = datetime_processing_params.get("default_timezone")

    work_timezone = gettz(timezone_name)

    if start_datetime is None:
        start_datetime = pd.Timestamp.now(tz=work_timezone)
    else:
        start_datetime = pd.Timestamp(start_datetime)
    if start_datetime.tzname() is None:
        start_datetime = start_datetime.replace(tzinfo=work_timezone)

    if end_datetime is None:
        end_datetime = start_datetime + time_tick.TIME_TICK
    else:
        end_datetime = pd.Timestamp(end_datetime)
    if end_datetime.tzname() is None:
        end_datetime = end_datetime.replace(tzinfo=work_timezone)

    predicted_boiler_temp_df = boiler_t_predictor.get_need_boiler_temp(start_datetime, end_datetime)

    predicted_boiler_temp_ds = []
    for _, row in predicted_boiler_temp_df.iterrows():
        datetime_ = row[column_names.TIMESTAMP]
        datetime_ = datetime_.astimezone(work_timezone)

        boiler_temp = row[column_names.FORWARD_PIPE_COOLANT_TEMP]
        boiler_temp = round(boiler_temp, 1)

        predicted_boiler_temp_ds.append((datetime_, boiler_temp))

    return predicted_boiler_temp_ds
