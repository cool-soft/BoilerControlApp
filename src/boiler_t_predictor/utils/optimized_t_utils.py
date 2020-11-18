
import config
from .io_utils import load_dataframe


def load_optimized_t_table(path=config.OPTIMIZED_T_TABLE_PATH):
    df = load_dataframe(path)
    return df
