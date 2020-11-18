
from datetime import datetime

import config
from boiler_t_predictor import ForecastWeatherTProvider


if __name__ == '__main__':

    t_provider = ForecastWeatherTProvider()

    min_date = datetime.now()
    max_date = min_date + (config.TIME_STEP * 10)
    a = t_provider.get_forecast_weather_t(min_date, max_date)
    print()

    b = t_provider.get_forecast_weather_t(min_date, max_date)
    print()
