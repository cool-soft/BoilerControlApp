
import json
import os
import pickle
from datetime import datetime

from config import (
    OPTIMIZED_T_TABLE_PATH
)
from modules.preprocess_utils import filter_by_timestamp


def load_optimized_t_table(path=OPTIMIZED_T_TABLE_PATH):
    df = load_dataframe(path)
    return df


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
