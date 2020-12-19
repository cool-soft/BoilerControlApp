
from datetime import datetime

from dataset_utils import data_consts
from weather_forecast_provider import WeatherForecastProvider


if __name__ == '__main__':

    t_provider = WeatherForecastProvider()

    min_date = datetime.now()
    max_date = min_date + (data_consts.TIME_TICK * 10)
    a = t_provider.get_weather_forecast(min_date, max_date)
    print(a)
