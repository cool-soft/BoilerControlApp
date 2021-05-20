import logging

import pandas as pd
from boiler.timedelta.io.abstract_sync_timedelta_loader \
    import AbstractSyncTimedeltaLoader
from dependency_injector import resources


class HeatingObjTimedeltaResource(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self,
             timedelta_loader: AbstractSyncTimedeltaLoader
             ) -> pd.DataFrame:
        timedelta_df = timedelta_loader.load_timedelta()
        return timedelta_df

    def shutdown(self, timedelta_df: pd.DataFrame):
        pass
