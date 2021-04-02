import pandas as pd


class TempRequirementsService:

    async def update_temp_requirements(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp):
        raise NotImplementedError
