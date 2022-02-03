import pandas as pd

from backend.db.conteiners import create_db_container
from backend.db.resources import PredictedBase
from backend.db.schemas import PredictedData


def add_predicted_to_db(control_actions_df: pd.DataFrame):
    db_container = create_db_container(path="predicted_data.db",
                                       base=PredictedBase)
    for i in range(len(control_actions_df)):
        data: PredictedData = PredictedData.parse_obj(control_actions_df.loc[i])
        db_container.db_repository().add_predicted(data=data)
        print(f"[DB INFO]  [new record added]: Time: {data.timestamp}  Temperature: {data.forward_temp}")
