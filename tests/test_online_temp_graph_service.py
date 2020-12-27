import pandas as pd

from containers.services_containers.online_temp_graph_container import OnlineTempGraphContainer
import column_names

if __name__ == '__main__':
    config = {
        "server_address": "https://lysva.agt.town/",
        "update_interval": 86400
    }

    temp_graph_container = OnlineTempGraphContainer(config=config)
    temp_graph_service = temp_graph_container.temp_graph_service()
    temp_graph = temp_graph_service.get_temp_graph()

    assert isinstance(temp_graph, pd.DataFrame)
    assert column_names.WEATHER_TEMP in temp_graph.columns
    assert column_names.REQUIRED_TEMP_AT_HOME_IN in temp_graph.columns
    assert column_names.REQUIRED_TEMP_AT_HOME_OUT in temp_graph.columns
    assert len(temp_graph) > 0
