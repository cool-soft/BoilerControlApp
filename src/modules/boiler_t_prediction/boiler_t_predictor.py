
from modules import consts


class BoilerTPredictor:

    def __init__(self):
        self._optimized_t_table = None
        self._homes_time_deltas = None
        self._temp_graph = None
        self._home_t_dispersion_coefficient = 1

    def set_homes_time_deltas(self, homes_time_deltas):
        self._homes_time_deltas = homes_time_deltas

    def set_optimized_t_table(self, t_table):
        self._optimized_t_table = t_table

    def set_temp_graph(self, temp_graph):
        self._temp_graph = temp_graph

    def set_dispersion_coefficient(self, coefficient):
        self._home_t_dispersion_coefficient = coefficient

    def predict_on_weather_t_arr(self, weather_t_arr):
        predicted_boiler_t = []
        max_home_time_delta = self._homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()
        t_count = len(weather_t_arr) - max_home_time_delta
        for t_idx in range(t_count):
            need_t_by_homes = self._get_need_t_in_homes(t_idx, weather_t_arr)
            need_boiler_t = self._calc_need_boiler_t_by_homes_t(need_t_by_homes)
            predicted_boiler_t.append(need_boiler_t)

        return predicted_boiler_t

    def _get_need_t_in_homes(self, t_idx, weather_t_arr):
        need_temps = {}
        for index, row in self._homes_time_deltas.iterrows():
            home_time_delta = row[consts.TIME_DELTA_COLUMN_NAME]
            home_name = row[consts.HOME_NAME_COLUMN_NAME]

            weather_t = weather_t_arr[t_idx + home_time_delta]
            need_t = self._get_need_t_by_temp_graph(weather_t)
            need_temps[home_name] = need_t

        return need_temps

    def _get_need_t_by_temp_graph(self, weather_t):
        available_t_condition = self._temp_graph[consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        need_t_in_home_by_t_graph = available_t[consts.HOME_T_COLUMN_NAME].min()
        need_t_in_home = need_t_in_home_by_t_graph * self._home_t_dispersion_coefficient
        return need_t_in_home

    def _calc_need_boiler_t_by_homes_t(self, need_t_by_homes):
        iterator = iter(need_t_by_homes.items())
        home_name, need_home_t = next(iterator)
        need_t_condition = self._optimized_t_table[home_name] >= need_home_t
        for home_name, need_home_t in iterator:
            need_t_condition = need_t_condition & (self._optimized_t_table[home_name] >= need_home_t)

        need_boiler_t = self._optimized_t_table[need_t_condition][consts.BOILER_NAME_COLUMN_NAME].min()
        return need_boiler_t
