import pandas as pd


class BoilerTempPredictionService:

    def get_need_boiler_temp(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp) -> pd.DataFrame:
        raise NotImplementedError
