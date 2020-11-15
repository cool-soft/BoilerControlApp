
from matplotlib import pyplot as plt
from datetime import datetime

import config
from modules.forecast_weather_t_provider import ForecastWeatherTProvider
from modules.boiler_t_predictor import BoilerTPredictor
from modules.home_deltas_utils import load_homes_time_deltas
from modules.io_utils import load_optimized_t_table
from modules.t_graph_utils import load_t_graph


if __name__ == '__main__':
    min_date = datetime.now()
    max_date = min_date + (60 * config.TIME_STEP)

    prediction_step = 5

    homes_time_deltas = load_homes_time_deltas()
    optimized_t_table = load_optimized_t_table()
    temp_graph = load_t_graph()

    weather_t_provider = ForecastWeatherTProvider()
    weather_t_df = weather_t_provider.get_forecast_weather_t(min_date, max_date)
    weather_t = weather_t_df[config.WEATHER_T_COLUMN_NAME].to_numpy()

    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_prediction_step(prediction_step)
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)

    predicted_boiler_t = boiler_t_predictor.predict_on_weather_t_arr(weather_t)
    dates = weather_t_df[config.TIMESTAMP_COLUMN_NAME].to_list()
    dates = dates[:len(predicted_boiler_t)]

    plt.plot(dates, predicted_boiler_t, label="Predicted boiler t")
    plt.plot(dates, weather_t[:len(predicted_boiler_t)], label="Weather t")

    plt.legend()
    plt.show()
