import pandas as pd
from boiler.timedelta.io.sync_timedelta_csv_reader import SyncTimedeltaCSVReader
from boiler.timedelta.io.sync_timedelta_file_loader import SyncTimedeltaFileLoader


def heating_system_correlation_table(filepath: str) -> pd.DataFrame:
    temp_correlation_table = pd.read_pickle(filepath)
    return temp_correlation_table


def heating_objects_timedelta(filepath: str) -> pd.DataFrame:
    loader = SyncTimedeltaFileLoader(filepath, reader=SyncTimedeltaCSVReader(separator=","))
    timedelta_df = loader.load_timedelta()
    return timedelta_df
