import logging
from typing import Optional

from dateutil.tz import gettz
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from constants import column_names
from services.boiler_temp_prediction_service.boiler_temp_prediction_service \
    import BoilerTempPredictionService
from containers.core import Core
from containers.services import Services
from endpoints.dependencies import InputDatesRange

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
@inject
def get_predicted_boiler_t(
        dates_range: InputDatesRange = Depends(),
        timezone_name: Optional[str] = None,
        boiler_t_predictor: BoilerTempPredictionService = Depends(
            Provide[Services.boiler_temp_prediction.boiler_temp_prediction_service]
        ),
        datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    Принимает 3 **опциональных** параметра.
    - **start_date**: Дата время начала управляющего воздействия (формат см. в конфигах).
    - **end_date**: Дата время окончания управляющего воздействия (формат см. в конфигах).
    - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
    По-умолчанию берется из конфигов.
    """
    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler t for dates range "
                  f"from {dates_range.start_date} to {dates_range.end_date} "
                  f"with timezone_name {timezone_name}")

    if timezone_name is None:
        timezone_name = datetime_processing_params.get("default_timezone")

    predicted_boiler_temp_df = boiler_t_predictor.get_need_boiler_temp(dates_range.start_date, dates_range.end_date)

    datetimes = predicted_boiler_temp_df[column_names.TIMESTAMP]
    work_timezone = gettz(timezone_name)
    datetimes = datetimes.dt.tz_convert(work_timezone)
    response_datetime_pattern = datetime_processing_params.get("response_pattern")
    datetimes = datetimes.dt.strftime(response_datetime_pattern)
    datetimes = datetimes.to_list()

    boiler_out_temps = predicted_boiler_temp_df[column_names.FORWARD_PIPE_COOLANT_TEMP].round(1)
    boiler_out_temps = boiler_out_temps.to_list()

    predicted_boiler_temp_list = []
    for datetime_, boiler_out_temp in zip(datetimes, boiler_out_temps):
        predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

    return predicted_boiler_temp_list
