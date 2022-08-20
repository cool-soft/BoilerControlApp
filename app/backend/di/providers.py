from boiler.temp_requirements.calculators.abstract_temp_requirements_calculator import \
    AbstractTempRequirementsCalculator
from boiler.temp_requirements.calculators.temp_graph_requirements_calculator import TempGraphRequirementsCalculator


def temp_requirements_calculator_factory(temp_graph_loader,
                                         weather_temp_round_algo
                                         ) -> AbstractTempRequirementsCalculator:
    return TempGraphRequirementsCalculator(
        temp_graph_loader.load_temp_graph(),
        weather_temp_round_algo
    )
