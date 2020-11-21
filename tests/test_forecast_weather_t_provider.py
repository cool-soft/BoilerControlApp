
from datetime import datetime

import consts
from boiler_t_prediction.forecast_weather_t_provider import ForecastWeatherTProvider


if __name__ == '__main__':

    t_provider = ForecastWeatherTProvider()

    min_date = datetime.now()
    max_date = min_date + (consts.TIME_STEP * 10)
    a = t_provider.get_forecast_weather_t(min_date, max_date)
    print(a)
