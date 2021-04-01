import pandas as pd


class TempGraphService:

    async def get_temp_graph(self) -> pd.DataFrame:
        raise NotImplementedError
