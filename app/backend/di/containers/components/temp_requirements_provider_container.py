from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Callable

from backend.di.providers import temp_requirements_calculator_factory
from backend.providers.temp_requirements_provider import TempRequirementsProvider


class TempRequirementsProviderContainer(DeclarativeContainer):
    weather_forecast_loader = Dependency()
    temp_graph_loader = Dependency()

    weather_temp_round_algo = Factory(ArithmeticFloatRoundAlgorithm)
    requirements_calculator = Callable(
        temp_requirements_calculator_factory,
        temp_graph_loader=temp_graph_loader,
        weather_temp_round_algo=weather_temp_round_algo
    )
    temp_requirements_provider = Factory(
        TempRequirementsProvider,
        weather_forecast_loader=weather_forecast_loader,
        temp_requirements_calculator=requirements_calculator
    )
