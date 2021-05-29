import pandas as pd
from boiler.data_processing.beetween_filter_algorithm import FullClosedTimestampFilterAlgorithm
from boiler.data_processing.timestamp_interpolator_algorithm import TimestampInterpolationAlgorithm
from boiler.data_processing.timestamp_round_algorithm import CeilTimestampRoundAlgorithm
from boiler.data_processing.value_interpolation_algorithm \
    import LinearInsideValueInterpolationAlgorithm, LinearOutsideValueInterpolationAlgorithm
from boiler_softm.constants.time_tick import TIME_TICK
from boiler_softm.weather.processing import SoftMWeatherProcessor
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Object, Dependency

from backend.services.weather_forecast_update_service.weather_forecast_service \
    import SimpleWeatherForecastService


class WeatherForecastContainer(DeclarativeContainer):
    weather_forecast_repository = Dependency()
    weather_forecast_loader = Dependency()

    timestamp_round_algorithm = Factory(
        CeilTimestampRoundAlgorithm,
        round_step=TIME_TICK
    )
    weather_forecast_preprocessor = Factory(
        SoftMWeatherProcessor,
        timestamp_round_algorithm=timestamp_round_algorithm,
        timestamp_interpolation_algorithm=Factory(
            TimestampInterpolationAlgorithm,
            timestamp_round_algorithm,
            TIME_TICK
        ),
        timestamp_filter_algorithm=Factory(FullClosedTimestampFilterAlgorithm),
        border_values_interpolation_algorithm=Factory(LinearInsideValueInterpolationAlgorithm),
        internal_values_interpolation_algorithm=Factory(LinearOutsideValueInterpolationAlgorithm)
    )

    weather_forecast_service = Factory(
        SimpleWeatherForecastService,
        weather_forecast_loader=weather_forecast_loader,
        weather_forecast_processor=weather_forecast_preprocessor,
        weather_forecast_repository=weather_forecast_repository,
        preload_timedelta=Object(pd.Timedelta(hours=3)),
        executor=None
    )
