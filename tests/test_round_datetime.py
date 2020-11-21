import consts
from dataset_utils.preprocess_utils import round_datetime
from datetime import datetime

if __name__ == '__main__':
    datetime_ = datetime.now()
    rounded_datetime = round_datetime(datetime_)

    print(datetime_, rounded_datetime, consts.TIME_STEP.total_seconds())
