
from datetime import datetime
from modules.real_weather_t_provider import RealWeatherTProvider


if __name__ == '__main__':

    t_provider = RealWeatherTProvider()

    min_date = datetime(2020, 10, 1)
    max_date = datetime(2020, 10, 3)
    a = t_provider.get_real_weather_t(min_date, max_date)
    print(1)

    min_date = datetime(2020, 10, 2)
    max_date = datetime(2020, 10, 4)
    b = t_provider.get_real_weather_t(min_date, max_date)
    print(2)
