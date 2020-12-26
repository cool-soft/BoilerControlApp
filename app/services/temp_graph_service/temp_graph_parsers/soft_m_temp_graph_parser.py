import pandas as pd

from .temp_graph_parser import TempGraphParser


class SoftMTempGraphParser(TempGraphParser):

    def __init__(self,
                 soft_m_weather_column_name,
                 soft_m_required_t_at_home_in_column_name,
                 soft_m_required_t_at_home_out_column_name,
                 weather_t_column_name,
                 required_t_at_home_in_column_name,
                 required_t_at_home_out_column_name):

        self._weather_t_column_name = weather_t_column_name
        self._required_t_at_home_in_column_name = required_t_at_home_in_column_name
        self._required_t_at_home_out_column_name = required_t_at_home_out_column_name

        self._soft_m_weather_column_name = soft_m_weather_column_name
        self._soft_m_required_t_at_home_in_column_name = soft_m_required_t_at_home_in_column_name
        self._soft_m_required_t_at_home_out_column_name = soft_m_required_t_at_home_out_column_name

    def parse_temp_graph(self, temp_graph_as_text):
        df = pd.read_json(temp_graph_as_text)
        df.rename(
            columns={
                self._soft_m_weather_column_name: self._weather_t_column_name,
                self._soft_m_required_t_at_home_in_column_name: self._required_t_at_home_in_column_name,
                self._soft_m_required_t_at_home_out_column_name: self._required_t_at_home_out_column_name
            },
            inplace=True)
        print(df)
        return df
