import pandas as pd


class BoilerTPredictorService:

    def get_need_boiler_t(self, start_datetime, end_datetime) -> pd.DataFrame:
        raise NotImplementedError
