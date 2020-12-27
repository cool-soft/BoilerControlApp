import pandas as pd


class BoilerTempPredictionService:

    def get_need_boiler_t(self, start_datetime, end_datetime) -> pd.DataFrame:
        raise NotImplementedError
