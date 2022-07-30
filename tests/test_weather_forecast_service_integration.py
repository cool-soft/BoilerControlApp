from datetime import timedelta, datetime

import pytest
from boiler_softm_lysva.constants.time_tick import TIME_TICK
from boiler_softm_lysva.weather.io \
    import SoftMLysvaSyncWeatherForecastOnlineLoader, SoftMLysvaSyncWeatherForecastOnlineReader
from boiler_softm_lysva.weather.processing import SoftMLysvaWeatherForecastProcessor
from dateutil.tz import gettz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import WeatherForecast
from backend.repositories.weather_forecast_repository import WeatherForecastRepository
from backend.services.weather_forecast_service import WeatherForecastService


class TestWeatherForecastService:
    time_tick = TIME_TICK
    timezone = gettz("Asia/Yekaterinburg")
    db_url = "sqlite:///:memory:"
    preload_timedelta = timedelta(minutes=10)

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            WeatherForecast.metadata.drop_all(conn)
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
            preload_timedelta=self.preload_timedelta
        )

    def test_weather_forecast_service_integration(self,
                                                  weather_forecast_update_service,
                                                  weather_forecast_repository,
                                                  session_factory):
        datetime_now = datetime.now(tz=self.timezone)
        weather_forecast_update_service.update_weather_forecast()
        with session_factory.begin():
            loaded_weather_forecast = weather_forecast_repository.get_weather_forecast_by_timestamp_range(
                datetime_now,
                datetime_now + self.preload_timedelta
            )
        assert not loaded_weather_forecast.empty
