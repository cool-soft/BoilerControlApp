
import json
import pickle


def load_dataframe(path):
    with open(path, "rb") as f:
        df = pickle.load(f)
    return df


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data
