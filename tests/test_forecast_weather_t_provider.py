
from datetime import datetime

import column_names
import time_tick
from services.weather_service.online_soft_m_weather_service import OnlineSoftMWeatherService


if __name__ == '__main__':

    t_provider = OnlineSoftMWeatherService()

    min_date = datetime.now()
    max_date = min_date + (time_tick.TIME_TICK * 10)
    a = t_provider.get_weather(min_date, max_date)
    print(a)
