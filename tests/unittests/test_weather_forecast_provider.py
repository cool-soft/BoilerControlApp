import pandas as pd
import pytest
from boiler.constants import column_names
from boiler_softm_lysva.constants.time_tick import TIME_TICK
from boiler_softm_lysva.weather.io \
    import SoftMLysvaSyncWeatherForecastOnlineLoader, SoftMLysvaSyncWeatherForecastOnlineReader
from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dateutil import tz

from backend.providers.weather_forecast_provider import WeatherForecastProvider


class TestWeatherForecastProvider:
    db_url = "sqlite:///:memory:"
    preload_timedelta = pd.Timedelta(minutes=10)
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

    def test_weather_forecast_provider(self, weather_forecast_provider):
        start_timestamp = pd.Timestamp.now(tz=tz.UTC)
        end_timestamp = start_timestamp+self.preload_timedelta
        weather_forecast = weather_forecast_provider.load_weather(start_timestamp, end_timestamp)
        assert not weather_forecast.empty
        assert start_timestamp <= weather_forecast[column_names.TIMESTAMP].min() <= start_timestamp + self.time_tick
        assert end_timestamp - self.time_tick <= weather_forecast[column_names.TIMESTAMP].max() < end_timestamp
