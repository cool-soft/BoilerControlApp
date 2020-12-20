import pandas as pd


class TempGraphService:

    def get_temp_graph(self) -> pd.DataFrame:
        raise NotImplementedError

    def get_required_t_at_home_in(self, weather_t):
        raise NotImplementedError
