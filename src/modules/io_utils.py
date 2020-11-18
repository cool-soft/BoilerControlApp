
import pickle


def load_dataframe(path):
    with open(path, "rb") as f:
        df = pickle.load(f)
    return df
