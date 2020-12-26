from dependency_injector import containers, providers

from resources.home_time_deltas_resource import HomeTimeDeltasResource
from resources.optimized_t_table_resource import OptimizedTTableResource
from services.boiler_t_predictor_service.simple_boiler_t_predictor_service import SimpleBoilerTPredictorService
from services.temp_graph_service.temp_graph_parsers.soft_m_temp_graph_parser import SoftMTempGraphParser
from services.temp_graph_service.online_soft_m_temp_graph_service import OnlineSoftMTempGraphService
from services.temp_requirements_service.simple_temp_requirements_service import SimpleTempRequirementsService
from services.weather_service.online_soft_m_weather_service import OnlineSoftMWeatherService
import data_consts
from services.weather_service.weather_data_parsers.soft_m_weather_parser import SoftMWeatherDataParser


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    optimized_t_table = providers.Resource(
        OptimizedTTableResource,
        config.boiler_t_prediction_service.optimized_t_table_path
    )

    homes_time_deltas = providers.Resource(
        HomeTimeDeltasResource,
        config.boiler_t_prediction_service.homes_deltas_path
    )

    weather_data_parser = providers.Singleton(
        SoftMWeatherDataParser,
        soft_m_weather_column_name=data_consts.SOFT_M_WEATHER_T_COLUMN_NAME,
        soft_m_date_column_name=data_consts.SOFT_M_DATE_COLUMN_NAME,
        soft_m_time_column_name=data_consts.SOFT_M_TIME_COLUMN_NAME,
        timestamp_column_name=data_consts.TIMESTAMP_COLUMN_NAME,
        weather_t_column_name=data_consts.WEATHER_T_COLUMN_NAME,
        weather_data_timezone_name=config.weather_forecast_service.server_timezone
    )
    weather_service = providers.Singleton(
        OnlineSoftMWeatherService,
        server_address=config.weather_forecast_service.server_address,
        update_interval=config.weather_forecast_service.update_interval,
        weather_data_parser=weather_data_parser
    )

    temp_graph_parser = providers.Singleton(
        SoftMTempGraphParser,
        soft_m_weather_column_name=data_consts.SOFT_M_TEMP_GRAPH_WEATHER_COLUMN_NAME,
        soft_m_required_t_at_home_in_column_name=data_consts.SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_IN_COLUMN_NAME,
        soft_m_required_t_at_home_out_column_name=data_consts.SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_OUT_COLUMN_NAME,
        weather_t_column_name=data_consts.WEATHER_T_COLUMN_NAME,
        required_t_at_home_in_column_name=data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME,
        required_t_at_home_out_column_name=data_consts.REQUIRED_T_AT_HOME_OUT_COLUMN_NAME
    )

    temp_graph_service = providers.Singleton(
        OnlineSoftMTempGraphService,
        server_address=config.temp_graph_service.server_address,
        update_interval=config.temp_graph_service.update_interval,
        temp_graph_parser=temp_graph_parser
    )

    temp_requirements_service = providers.Singleton(
        SimpleTempRequirementsService,
        temp_graph_service=temp_graph_service,
        weather_service=weather_service
    )

    boiler_t_predictor_service = providers.Singleton(
        SimpleBoilerTPredictorService,
        optimized_t_table=optimized_t_table,
        home_time_deltas=homes_time_deltas,
        temp_requirements_service=temp_requirements_service,
        home_t_dispersion_coefficient=config.boiler_t_prediction_service.home_t_dispersion_coefficient
    )
