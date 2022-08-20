from boiler_softm_lysva.temp_graph.io import SoftMLysvaSyncTempGraphOnlineReader, SoftMLysvaSyncTempGraphOnlineLoader
from boiler_softm_lysva.weather.io import \
    SoftMLysvaSyncWeatherForecastOnlineReader, \
    SoftMLysvaSyncWeatherForecastOnlineLoader
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Configuration


class Gateways(DeclarativeContainer):
    config = Configuration(strict=True)

    weather_forecast_reader = Factory(SoftMLysvaSyncWeatherForecastOnlineReader)
    weather_forecast_loader = Factory(
        SoftMLysvaSyncWeatherForecastOnlineLoader,
        reader=weather_forecast_reader
    )

    temp_graph_reader = Factory(SoftMLysvaSyncTempGraphOnlineReader)
    temp_graph_loader = Factory(
        SoftMLysvaSyncTempGraphOnlineLoader,
        reader=temp_graph_reader
    )
