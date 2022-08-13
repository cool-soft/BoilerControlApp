from datetime import timedelta, datetime

import pandas as pd
import pytest
from boiler.constants import column_names, circuit_types
from boiler.control_action.predictors.single_circuit_control_action_predictor import SingleCircuitControlActionPredictor
from boiler.control_action.temp_delta_calculator.single_type_temp_delta_calculator import SingleTypeTempDeltaCalculator
from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from boiler.data_processing.timestamp_round_algorithm import FloorTimestampRoundAlgorithm
from boiler.heating_system.model.corr_table_heating_system_model import CorrTableHeatingSystemModel
from boiler.heating_system.model_requirements.corr_table_model_requirements import CorrTableModelRequirements
from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator
from boiler_softm_lysva.constants.time_tick import TIME_TICK
from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from boiler_softm_lysva.weather.io import SoftMLysvaSyncWeatherForecastOnlineReader, \
    SoftMLysvaSyncWeatherForecastOnlineLoader
from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dateutil import tz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import ControlAction, WeatherForecast
from backend.repositories.control_action_repository import ControlActionRepository
from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.services.control_action_prediction_service import ControlActionPredictionService
from backend.providers.weather_forecast_provider import WeatherForecastService


class TestControlActionPredictServiceIntegration:
    time_tick = TIME_TICK
    weather_forecast_preload_timedelta = timedelta(hours=3)
    timedelta_predict_forward = timedelta(seconds=3600)
    min_boiler_temp = 30
    max_boiler_temp = 90
    boiler_temp_step = 1

    db_url = "sqlite:///:memory:"

    timedelta_df = pd.DataFrame([
        {column_names.HEATING_OBJ_ID: "obj_1",
         column_names.AVG_TIMEDELTA: pd.Timedelta(seconds=600)},
        {column_names.HEATING_OBJ_ID: "obj_2",
         column_names.AVG_TIMEDELTA: pd.Timedelta(seconds=1200)},
    ])

    @pytest.fixture
    def correlation_df(self):
        max_timedelta = self.timedelta_df[column_names.AVG_TIMEDELTA].max().total_seconds()
        corr_list = []
        for boiler_temp in range(self.min_boiler_temp,
                                 self.max_boiler_temp + self.boiler_temp_step,
                                 self.boiler_temp_step):
            corr_row = {}
            for _, row in self.timedelta_df.iterrows():
                corr_row[column_names.CORRELATED_BOILER_TEMP] = boiler_temp
                corr_row[row[column_names.HEATING_OBJ_ID]] = \
                    boiler_temp - (row[column_names.AVG_TIMEDELTA].total_seconds()/max_timedelta*0.5*boiler_temp)
            corr_list.append(corr_row)
        df = pd.DataFrame(corr_list)
        return df

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            ControlAction.metadata.drop_all(conn)
            WeatherForecast.metadata.drop_all(conn)
            ControlAction.metadata.create_all(conn)
            WeatherForecast.metadata.create_all(conn)
        db_session_maker = sessionmaker(
            autocommit=False,
            bind=engine
        )
        session_factory = scoped_session(
            db_session_maker
        )
        return session_factory

    @pytest.fixture
    def weather_forecast_repository(self, session_factory):
        return WeatherForecastRepository(session_factory)

    @pytest.fixture
    def weather_forecast_reader(self):
        return SoftMLysvaSyncWeatherForecastOnlineReader()

    @pytest.fixture
    def weather_forecast_loader(self, weather_forecast_reader, is_need_proxy, proxy_address):
        http_proxy = None
        https_proxy = None
        if is_need_proxy:
            http_proxy = proxy_address
            https_proxy = proxy_address
        return SoftMLysvaSyncWeatherForecastOnlineLoader(
            reader=weather_forecast_reader,
            http_proxy=http_proxy,
            https_proxy=https_proxy
        )

    @pytest.fixture
    def weather_forecast_processor(self):
        return SoftMLysvaWeatherForecastProcessor()

    @pytest.fixture
    def weather_forecast_update_service(self,
                                        session_factory,
                                        weather_forecast_repository,
                                        weather_forecast_loader,
                                        weather_forecast_processor
                                        ):
        return WeatherForecastService(
            weather_forecast_loader,
            weather_forecast_processor,
            weather_forecast_repository,
            session_factory,
            preload_timedelta=self.weather_forecast_preload_timedelta
        )

    @pytest.fixture
    def control_action_repository(self, session_factory):
        return ControlActionRepository(session_factory)

    @pytest.fixture
    def temp_graph_reader(self):
        return SoftMLysvaSyncTempGraphOnlineReader()

    @pytest.fixture
    def temp_graph_loader(self, temp_graph_reader, is_need_proxy, proxy_address):
        http_proxy = None
        https_proxy = None
        if is_need_proxy:
            http_proxy = proxy_address
            https_proxy = proxy_address
        loader = SoftMLysvaSyncTempGraphOnlineLoader(
            reader=temp_graph_reader,
            http_proxy=http_proxy,
            https_proxy=https_proxy
        )
        return loader

    @pytest.fixture
    def temp_requirements_calculator(self, temp_graph_loader):
        return TempGraphRequirementsCalculator(
            temp_graph=temp_graph_loader.load_temp_graph(),
            weather_temp_round_algorithm=ArithmeticFloatRoundAlgorithm()
        )

    @pytest.fixture
    def model_requirements(self):
        return CorrTableModelRequirements(
            timedelta_df=self.timedelta_df
        )

    @pytest.fixture
    def heating_system_model(self, correlation_df):
        return CorrTableHeatingSystemModel(
            correlation_df,
            self.timedelta_df
        )

    @pytest.fixture
    def temp_delta_calculator(self):
        return SingleTypeTempDeltaCalculator()

    @pytest.fixture
    def control_action_predictor(self, heating_system_model, temp_delta_calculator):
        return SingleCircuitControlActionPredictor(
            heating_system_model,
            temp_delta_calculator
        )

    @pytest.fixture
    def timestamp_round_algo(self):
        return FloorTimestampRoundAlgorithm(self.time_tick)

    @pytest.fixture
    def control_action_predict_service(self,
                                       session_factory,
                                       weather_forecast_repository,
                                       model_requirements,
                                       temp_requirements_calculator,
                                       control_action_predictor,
                                       control_action_repository,
                                       timestamp_round_algo,
                                       ):
        return ControlActionPredictionService(
            session_factory,
            weather_forecast_repository,
            model_requirements,
            temp_requirements_calculator,
            control_action_predictor,
            control_action_repository,
            timestamp_round_algo,
            self.time_tick,
            self.timedelta_predict_forward
        )

    def test_update_weather_and_update_control(self,
                                               session_factory,
                                               control_action_repository,
                                               control_action_predict_service,
                                               weather_forecast_update_service,
                                               ):
        control_action_start_timestamp = datetime.now(tz.UTC)
        control_action_end_timestamp = control_action_start_timestamp + self.timedelta_predict_forward + self.time_tick
        weather_forecast_update_service.update_weather_forecast()
        control_action_predict_service.update_control_actions()
        with session_factory():
            control_action_df = control_action_repository.get_control_action(
                control_action_start_timestamp,
                control_action_end_timestamp,
                circuit_types.HEATING
            )
        assert len(control_action_df) == self.timedelta_predict_forward / self.time_tick
