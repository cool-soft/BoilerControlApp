from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from backend.constants import config_names
from backend.controllers.dependencies import \
    InputDatetimeRange, \
    InputTimezone, \
    get_temp_requirements_coefficient, \
    get_max_boiler_temp, \
    get_min_boiler_temp
from backend.di.containers.services import Services
from backend.logging import logger
from backend.models.api import ControlActionV3, SettingV3
from backend.services.control_action_report_service import ControlActionReportService
from backend.services.settings_service import SettingsService

api_router = APIRouter(prefix="/api/v3")


# noinspection PyTypeChecker
@api_router.get("/predictedBoilerTemp", response_model=List[ControlActionV3])
@inject
def get_predicted_boiler_temp(
        datetime_range: InputDatetimeRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        control_action_report_service: ControlActionReportService = Depends(
            Provide[Services.control_action_pkg.control_action_report_service]
        )
):
    # noinspection SpellCheckingInspection
    """
            Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
            Принимает 3 **опциональных** параметра.
            - **start_datetime**: Дата время начала управляющего воздействия в формате ISO 8601.
            - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO 8601.
            - **weather_data_timezone**: Имя временной зоны для обработки запроса и генерации ответа.
            Если не указан - используется временная зона из конфигов.

            ISO 8601: https://en.wikipedia.org/wiki/ISO_8601

            Временные зоны: см. «TZ database name» https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

            ---
            Формат времени в запросе:
            - YYYY-MM-DD?HH:MM[:SS[.fffffff]][+HH:MM] где ? это T или символ пробела.

            Примеры:
            - 2020-01-30T00:17:01.1234567+05:00 - Для обработки датывремени используется временная зона из самой строки,
            формат «O» в C#.
            - 2020-01-30 00:17:07+05:00 - Для обработки даты и времени используется временная зона из самой строки.
            - 2020-01-30 00:17+05:30 - Для обработки даты и времени используется временная зона из самой строки.
            - 2020-01-30 00:17+05 - Для обработки даты и времени используется временная зона из самой строки.
            - 2020-01-30 00:17 - Используется временная зона из параметра weather_data_timezone.
            """

    logger.debug(f"Requested predicted boiler temp for dates range "
                 f"from {datetime_range.start_datetime} to {datetime_range.end_datetime} "
                 f"with weather_data_timezone {work_timezone.name}")

    control_action_list = control_action_report_service.report_v3(
        datetime_range.start_datetime,
        datetime_range.end_datetime,
        work_timezone.timezone
    )
    return control_action_list


# noinspection PyTypeChecker
@api_router.get("/settings", response_model=List[SettingV3])
@inject
def get_settings(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    """
    Возвращает список ключ-значение всех динамических настроек
    """
    return settings_service.get_all_settings()


@api_router.put("/settings/apartmentHouseMinTempCoefficient",
                status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response)
@inject
def put_apartment_house_min_temp_coefficient(
        coefficient: float = Depends(get_temp_requirements_coefficient),
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    settings_service.set_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT, coefficient)


@api_router.get("/settings/apartmentHouseMinTempCoefficient", response_model=SettingV3)
@inject
def get_apartment_house_min_temp_coefficient(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    """
    Возвращает текущее значение коэффициента требований температурного графика в МКД.
    """
    return settings_service.get_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT)


@api_router.put("/settings/maxBoilerTemp",
                status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response)
@inject
def put_max_boiler_temp(
        temp: float = Depends(get_max_boiler_temp),
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    settings_service.set_setting(config_names.MAX_BOILER_TEMP, temp)


@api_router.get("/settings/maxBoilerTemp", response_model=SettingV3)
@inject
def get_max_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    """
    Возвращает текущее значение макисмальной температуры на выходе из котельной.
    """
    return settings_service.get_setting(config_names.MAX_BOILER_TEMP)


@api_router.put("/settings/minBoilerTemp",
                status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response)
@inject
def put_min_boiler_temp(
        temp: float = Depends(get_min_boiler_temp),
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    settings_service.set_setting(config_names.MIN_BOILER_TEMP, temp)


@api_router.get("/settings/minBoilerTemp", response_model=SettingV3)
@inject
async def get_min_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    """
    Возвращает текущее значение минимальной температуры на выходе из котельной.
    """
    return settings_service.get_setting(config_names.MIN_BOILER_TEMP)


@api_router.put("/settings/modelErrorSize",
                status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response)
@inject
def put_model_error_size(
        value: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    settings_service.set_setting(config_names.MODEL_ERROR_SIZE, value)


@api_router.get("/settings/modelErrorSize", response_model=SettingV3)
@inject
def get_model_error_size(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    """
    Возвращает текущее значение поправки на ошибку модели.
    """
    return settings_service.get_setting(config_names.MODEL_ERROR_SIZE)
