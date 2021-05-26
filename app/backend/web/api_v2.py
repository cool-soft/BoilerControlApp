import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.constants import config_names
from backend.containers.services import Services
from backend.services.SettingsService import SettingsService
from backend.services.control_action_report_service.control_action_report_service import ControlActionReportService
from backend.web.dependencies import InputDatetimeRange, InputTimezone

api_router = APIRouter(prefix="/api/v2")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse)
@inject
async def get_predicted_boiler_temp(
        datetime_range: InputDatetimeRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        control_action_report_service: ControlActionReportService = Depends(
            Provide[Services.control_action_report_pkg.control_action_report_service]
        )
):
    # noinspection SpellCheckingInspection
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия в формате ISO 8601.
        - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO 8601.
        - **timezone**: Имя временной зоны для обработки запроса и генерации ответа.
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
        - 2020-01-30 00:17 - Используется временная зона из параметра timezone.

        ---
        Формат времени в ответе:
        - 2020-01-30T00:17:07+05:00 - Парсится при помощи DateTimeStyle.RoundtripKind в C#.
        При формировании ответа используется врменная зона из парметра timezone.
        """

    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler temp for dates range "
                  f"from {datetime_range.start_datetime} to {datetime_range.end_datetime} "
                  f"with timezone {work_timezone.name}")

    control_action = await control_action_report_service.report_v1(
        datetime_range.start_datetime,
        datetime_range.end_datetime,
        work_timezone.timezone
    )
    return control_action


@api_router.post("/setApartmentHouseMinTempCoefficient")
@inject
async def set_apartment_house_min_temp_coefficient(
        coefficient: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT, coefficient)


@api_router.post("/setMaxBoilerTemp")
@inject
async def set_max_boiler_temp(
        temp: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MAX_BOILER_TEMP, temp)


@api_router.post("/setMinBoilerTemp")
@inject
async def set_min_boiler_temp(
        temp: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MIN_BOILER_TEMP, temp)


@api_router.post("/setModelErrorSize")
@inject
async def set_model_error_size(
        value: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MODEL_ERROR_SIZE, value)


@api_router.get("/getApartmentHouseMinTempCoefficient")
@inject
async def get_apartment_house_min_temp_coefficient(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT)


@api_router.get("/getMaxBoilerTemp")
@inject
async def get_max_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MAX_BOILER_TEMP)


@api_router.get("/getMinBoilerTemp")
@inject
async def get_min_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MIN_BOILER_TEMP)


@api_router.get("/getModelErrorSize")
@inject
async def get_model_error_size(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MODEL_ERROR_SIZE)
