from boiler.data_processing.float_round_algorithm import ArithmeticFloatRoundAlgorithm
from boiler.temp_requirements.calculators.abstract_temp_requirements_calculator import \
    AbstractTempRequirementsCalculator
from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Callable

from backend.providers.temp_requirements_provider import TempRequirementsProvider


def temp_requirements_calculator(temp_graph_loader,
                                 weather_temp_round_algo
                                 ) -> AbstractTempRequirementsCalculator:
    return TempGraphRequirementsCalculator(
        temp_graph_loader.load_temp_graph(),
        weather_temp_round_algo
    )


class TempRequirementsProviderContainer(DeclarativeContainer):
    weather_forecast_loader = Dependency()
    temp_graph_loader = Dependency()

    weather_temp_round_algo = Factory(ArithmeticFloatRoundAlgorithm)
    requirements_calculator = Callable(
        temp_requirements_calculator,
        temp_graph_loader=temp_graph_loader,
        weather_temp_round_algo=weather_temp_round_algo
    )
    temp_requirements_provider = Factory(
        TempRequirementsProvider,
        weather_forecast_loader=weather_forecast_loader,
        temp_requirements_calculator=requirements_calculator
    )
