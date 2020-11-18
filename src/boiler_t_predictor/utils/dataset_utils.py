from boiler_t_predictor.utils.io_utils import load_dataframe
from boiler_t_predictor.utils.preprocess_utils import filter_by_timestamp


def load_dataset(path, start_date, end_date):
    df = load_dataframe(path)
    df = filter_by_timestamp(df, start_date, end_date)
    return df