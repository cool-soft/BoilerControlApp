import data_consts
from preprocess_utils import round_datetime
from datetime import datetime

if __name__ == '__main__':
    datetime_ = datetime.now()
    rounded_datetime = round_datetime(datetime_)

    print(datetime_, rounded_datetime, data_consts.TIME_TICK.total_seconds())
