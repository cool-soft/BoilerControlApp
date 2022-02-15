import pandas as pd

from backend.db.columns_names import WEATHER_COLUMNS, PREDICTED_COLUMNS
from backend.db.conteiners import create_db_container
from backend.db.resources import PredictedBase, WeatherBase
from backend.db.schemas import PredictedData, WeatherData


def add_predicted_to_db(control_actions_df: pd.DataFrame):
    """
    Добавление пронозных данных по котельной в БД
    :param control_actions_df: данные по прогнозу
    :return:
    """
    control_actions_df = control_actions_df.copy()
    control_actions_df.rename(columns=PREDICTED_COLUMNS, inplace=True)

    db_container = create_db_container(path="predicted_data.db",
                                       base=PredictedBase)
    for i in range(len(control_actions_df)):
        data: PredictedData = PredictedData.parse_obj(control_actions_df.loc[i])
        data.timestamp = data.timestamp.astimezone(tz="Asia/Yekaterinburg")
        db_container.db_repository().add_predicted(data=data)
        print(f"[DB INFO / Predicted]  [new record added]: Time: {data.timestamp}  Temperature: {data.forward_temp}")


def add_weather_to_db(predicted_weather_df: pd.DataFrame, rows: int = 21):
    predicted_weather_df = predicted_weather_df.copy()
    predicted_weather_df.rename(columns=WEATHER_COLUMNS, inplace=True)
    predicted_weather_df = predicted_weather_df[:rows]

    db_container = create_db_container(path="predicted_weather_data.db",
                                       base=WeatherBase)
    for i in range(len(predicted_weather_df)):
        data: WeatherData = WeatherData.parse_obj(predicted_weather_df.loc[i])
        data.d_timestamp = data.d_timestamp.astimezone(tz="Asia/Yekaterinburg")
        db_container.db_repository().add_weather(data=data)
        print(f"[DB INFO / Weather]  [new record added]: Time: {data.d_timestamp}  Temperature: {data.t}")
