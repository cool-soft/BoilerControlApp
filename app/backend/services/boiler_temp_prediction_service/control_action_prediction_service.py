import pandas as pd


class ControlActionPredictionService:

    async def update_control_actions(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp):
        raise NotImplementedError
