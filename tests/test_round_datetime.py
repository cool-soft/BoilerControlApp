from dataset_utils import data_consts
from dataset_utils.preprocess_utils import round_datetime
from datetime import datetime

if __name__ == '__main__':
    datetime_ = datetime.now()
    rounded_datetime = round_datetime(datetime_)

    print(datetime_, rounded_datetime, data_consts.TIME_TICK.total_seconds())
