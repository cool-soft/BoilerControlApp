import pandas as pd
import pytest
from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator
from boiler_softm_lysva.constants.time_tick import TIME_TICK
from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from boiler_softm_lysva.weather.io import \
    SoftMLysvaSyncWeatherForecastOnlineLoader, \
    SoftMLysvaSyncWeatherForecastOnlineReader
from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dateutil import tz

from backend.providers.temp_requirements_provider import TempRequirementsProvider
from backend.providers.weather_forecast_provider import WeatherForecastProvider


class TestTempRequirementsProvider:
    db_url = "sqlite:///:memory:"
    calc_timedelta = pd.Timedelta(minutes=60)
    time_tick = TIME_TICK

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
    def weather_forecast_provider(self, weather_forecast_loader, weather_forecast_processor):
        return WeatherForecastProvider(
            weather_forecast_loader,
            weather_forecast_processor
        )

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
        return SoftMLysvaSyncTempGraphOnlineLoader(
            reader=temp_graph_reader,
            http_proxy=http_proxy,
            https_proxy=https_proxy
        )

    @pytest.fixture
    def temp_requirements_calculator(self, temp_graph_loader):
        temp_graph = temp_graph_loader.load_temp_graph()
        return TempGraphRequirementsCalculator(
            temp_graph,
            ArithmeticFloatRoundAlgorithm(decimals=1)
        )

    @pytest.fixture
    def temp_requirements_provider(self, temp_requirements_calculator, weather_forecast_provider):
        return TempRequirementsProvider(
            weather_forecast_provider,
            temp_requirements_calculator
        )

    def test_temp_requirements_provider(self, temp_requirements_provider):
        start_timestamp = pd.Timestamp.now(tz=tz.UTC)
        end_timestamp = start_timestamp+self.calc_timedelta
        temp_requirements = temp_requirements_provider.get_temp_requirements(start_timestamp, end_timestamp)

        assert isinstance(temp_requirements, pd.DataFrame)
        assert not temp_requirements.empty
