import pandas as pd

from boiler.constants import column_names
from backend.containers.services_containers.temp_graph_container import TempGraphContainer

if __name__ == '__main__':
    config = {
        "server_address": "https://lysva.agt.town/",
        "cache_lifetime": 86400
    }

    temp_graph_container = TempGraphContainer(config=config)
    temp_graph_service = temp_graph_container.temp_graph_update_service()
    temp_graph = temp_graph_service.predict_control_actions_async()

    assert isinstance(temp_graph, pd.DataFrame)
    assert column_names.WEATHER_TEMP in temp_graph.columns
    assert column_names.FORWARD_PIPE_COOLANT_TEMP in temp_graph.columns
    assert column_names.BACKWARD_PIPE_COOLANT_TEMP in temp_graph.columns
    assert len(temp_graph) > 0
