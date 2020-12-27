from datetime import datetime

import pandas as pd
from dateutil.tz import tzlocal

import time_tick
from containers.services_containers.online_weather_container import OnlineWeatherContainer
import column_names

if __name__ == '__main__':
    config = {
        "server_address": "https://lysva.agt.town/",
        "server_timezone": "Asia/Yekaterinburg",
        "update_interval": 600
    }

    start_datetime = datetime.now(tzlocal())
    end_datetime = start_datetime + (time_tick.TIME_TICK * 20)

    online_weather_container = OnlineWeatherContainer(config=config)
    online_weather_service = online_weather_container.weather_service()
    weather_data_df = online_weather_service.get_weather(start_datetime, end_datetime)

    assert isinstance(weather_data_df, pd.DataFrame)
    assert column_names.WEATHER_TEMP in weather_data_df.columns
    assert column_names.TIMESTAMP in weather_data_df.columns
    assert len(weather_data_df) > 0
