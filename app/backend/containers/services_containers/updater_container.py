import pandas as pd
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Singleton, Configuration, List, Callable
from updater.updater_service.simple_updater_service import SimpleUpdaterService

from backend.services.control_action_prediction_service.control_action_updatable_item import ControlActionUpdatableItem
from backend.services.temp_graph_update_service.temp_graph_updatable_item import TempGraphUpdatableItem
from backend.services.weather_forecast_update_service.weather_forecast_updatable_item import \
    WeatherForecastUpdatableItem


class UpdateContainer(DeclarativeContainer):
    config = Configuration(strict=True)
    
    control_actions_predictor = Dependency()
    temp_graph_updater = Dependency()
    weather_forecast_updater = Dependency()

    temp_graph_updatable_item = Singleton(
        TempGraphUpdatableItem,
        provider=temp_graph_updater.provider,
        update_interval=Callable(
            pd.Timedelta,
            seconds=config.update_intervals.temp_graph
        )
    )

    weather_forecast_updatable_item = Singleton(
        WeatherForecastUpdatableItem,
        provider=weather_forecast_updater.provider,
        update_interval=Callable(
            pd.Timedelta,
            seconds=config.update_intervals.weather_forecast
        )
    )

    control_action_updatable_item = Singleton(
        ControlActionUpdatableItem,
        provider=control_actions_predictor.provider,
        dependencies=List(
            temp_graph_updatable_item,
            weather_forecast_updatable_item
        )
    )

    updater_service = Singleton(
        SimpleUpdaterService,
        item_to_update=control_action_updatable_item
    )
