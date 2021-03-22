import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from constants import column_names
from containers.services import Services
from endpoints.dependencies import InputDatetimeRange, InputTimezone
from services.boiler_temp_prediction_service.boiler_temp_prediction_service import BoilerTempPredictionService

api_router = APIRouter(prefix="/api/v2")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse)
@inject
def get_predicted_boiler_t(
        datetime_range: InputDatetimeRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        boiler_temp_predictor: BoilerTempPredictionService = Depends(
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
                  f"from {datetime_range.start_datetime} to {datetime_range.end_datetime} "
                  f"with timezone_name {work_timezone.name}")

    # noinspection PyTypeChecker
    predicted_boiler_temp_df = boiler_temp_predictor.get_need_boiler_temp(
        datetime_range.start_datetime,
        datetime_range.end_datetime
    )

    if predicted_boiler_temp_df.empty:
        return []

    datetimes = predicted_boiler_temp_df[column_names.TIMESTAMP]
    datetimes = datetimes.dt.tz_convert(work_timezone.timezone)
    datetimes = datetimes.to_list()

    boiler_out_temps = predicted_boiler_temp_df[column_names.FORWARD_PIPE_COOLANT_TEMP].round(1)
    boiler_out_temps = boiler_out_temps.to_list()

    predicted_boiler_temp_list = []
    for datetime_, boiler_out_temp in zip(datetimes, boiler_out_temps):
        predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

    return predicted_boiler_temp_list
