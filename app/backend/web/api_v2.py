import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from boiler.constants import column_names
from backend.containers.services import Services
from backend.services.boiler_temp_prediction_service.control_action_prediction_service import ControlActionPredictionService
from backend.web.dependencies import InputDatetimeRange, InputTimezone

api_router = APIRouter(prefix="/api/v2")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse)
@inject
async def get_predicted_boiler_t(
        datetime_range: InputDatetimeRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        boiler_temp_predictor: ControlActionPredictionService = Depends(
            Provide[Services.boiler_temp_prediction.boiler_temp_prediction_service]
        )
):
    # noinspection SpellCheckingInspection
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия в формате ISO 8601.
        - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO 8601.
        - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
        Если не указан - используется временная зона из конфигов.

        ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
        Временные зоны: см. «TZ database name» https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

        ---
        Формат времени в запросе:
        - YYYY-MM-DD?HH:MM[:SS[.fffffff]][+HH:MM] где ? это T или символ пробела.

        Примеры:
        - 2020-01-30T00:17:01.1234567+05:00 - Для обработки даты и времени испсользуется временная зона из самой строки,
        формат «O» в C#.
        - 2020-01-30 00:17:07+05:00 - Для обработки даты и времени испсользуется временная зона из самой строки.
        - 2020-01-30 00:17+05:30 - Для обработки даты и времени испсользуется временная зона из самой строки.
        - 2020-01-30 00:17+05 - Для обработки даты и времени испсользуется временная зона из самой строки.
        - 2020-01-30 00:17 - Используется временная зона из параметра timezone_name.

        ---
        Формат времени в ответе:
        - 2020-01-30T00:17:07+05:00 - Парсится при помощи DateTimeStyle.RoundtripKind в C#.
        При формировании ответа используется врменная зона из парметра timezone_name.
        """

    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler temp for dates range "
                  f"from {datetime_range.start_datetime} to {datetime_range.end_datetime} "
                  f"with timezone_name {work_timezone.name}")

    # noinspection PyTypeChecker
    predicted_boiler_temp_df = await boiler_temp_predictor.update_control_actions(
        datetime_range.start_datetime,
        datetime_range.end_datetime
    )

    predicted_boiler_temp_list = []
    if not predicted_boiler_temp_df.empty:

        datetimes = predicted_boiler_temp_df[column_names.TIMESTAMP]
        datetimes = datetimes.dt.tz_convert(work_timezone.timezone)
        datetimes = datetimes.to_list()

        boiler_out_temps = predicted_boiler_temp_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
        boiler_out_temps = boiler_out_temps.round(1)
        boiler_out_temps = boiler_out_temps.to_list()

        for datetime_, boiler_out_temp in zip(datetimes, boiler_out_temps):
            predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

    return predicted_boiler_temp_list
