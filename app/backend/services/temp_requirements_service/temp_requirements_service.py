import pandas as pd


class TempRequirementsService:

    def get_required_temp(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp) -> pd.DataFrame:
        raise NotImplementedError
