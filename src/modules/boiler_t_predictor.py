import config


class BoilerTPredictor:

    def __init__(self):
        self._window_size = 5
        self._smooth_size = 2
        self._optimized_t_table = None
        self._homes_time_deltas = None
        self._temp_graph = None
        self._home_t_dispersion_coefficient = config.HOME_T_DISPERSION_COEFFICIENT

    def set_homes_time_deltas(self, homes_time_deltas):
        self._homes_time_deltas = homes_time_deltas

    def set_window_size(self, window_size):
        self._window_size = window_size

    def set_smooth_size(self, smooth_size):
        self._smooth_size = smooth_size

    def set_optimized_t_table(self, t_table):
        self._optimized_t_table = t_table

    def set_temp_graph(self, temp_graph):
        self._temp_graph = temp_graph

    def set_dispersion_coefficient(self, coefficient):
        self._home_t_dispersion_coefficient = coefficient

    def predict_on_weather_t_arr(self, weather_t_arr):
        print("Predicting")

        predicted_boiler_t = []
        start_t_idx = self._window_size - self._smooth_size - 1
        max_home_time_delta = self._homes_time_deltas["time_delta"].max()
        end_t_idx = len(weather_t_arr) - max_home_time_delta + self._smooth_size
        for t_idx in range(start_t_idx, end_t_idx, self._window_size):
            need_t_by_homes = self._get_need_t_in_homes(t_idx, weather_t_arr)
            need_boiler_t = self._calc_need_boiler_t_by_homes_t(need_t_by_homes)
            for i in range(self._window_size):
                predicted_boiler_t.append(need_boiler_t)
            print(f"Predicted {t_idx}/{end_t_idx}")

        return predicted_boiler_t

    def _get_need_t_in_homes(self, t_idx, weather_t_arr):
        need_temps = {}
        for index, row in self._homes_time_deltas.iterrows():
            home_time_delta = row[config.TIME_DELTA_COLUMN_NAME]
            home_name = row[config.HOME_NAME_COLUMN_NAME]

            weather_t = weather_t_arr[t_idx + home_time_delta]
            need_t = self._get_need_t_by_temp_graph(weather_t)
            need_temps[home_name] = need_t

        return need_temps

    def _get_need_t_by_temp_graph(self, weather_t):
        available_t = self._temp_graph[self._temp_graph[config.WEATHER_T_COLUMN_NAME] <= weather_t]
        need_t_in_home_by_t_graph = available_t[config.T_GRAPH_HOME_T_COLUMN_NAME].min()
        need_t = need_t_in_home_by_t_graph * self._home_t_dispersion_coefficient
        return need_t

    def _calc_need_boiler_t_by_homes_t(self, need_t_by_homes):
        iterator = iter(need_t_by_homes.items())
        home_name, home_need_t = next(iterator)
        need_t_condition = self._optimized_t_table[home_name] >= home_need_t
        for home_name, home_need_t in iterator:
            need_t_condition = need_t_condition & (self._optimized_t_table[home_name] >= home_need_t)

        need_boiler_t = self._optimized_t_table[need_t_condition]
        need_boiler_t = need_boiler_t[config.BOILER_COLUMN_NAME].min()
        return need_boiler_t
