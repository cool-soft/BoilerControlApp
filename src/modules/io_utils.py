
import json
import pickle

from modules.preprocess_utils import filter_by_timestamp


def load_dataset(path, start_date, end_date):
    df = load_dataframe(path)
    df = filter_by_timestamp(df, start_date, end_date)
    return df


def load_dataframe(path):
    with open(path, "rb") as f:
        df = pickle.load(f)
    return df


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data