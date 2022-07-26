import pandas as pd
from boiler.timedelta.io.abstract_sync_timedelta_loader \
    import AbstractSyncTimedeltaLoader
from dependency_injector import resources

from backend.logging import logger


class HeatingObjTimedeltaResource(resources.Resource):

    def init(self,
             loader: AbstractSyncTimedeltaLoader
             ) -> pd.DataFrame:
        logger.debug("Initialization of Resource")

        timedelta_df = loader.load_timedelta()
        return timedelta_df

    def shutdown(self, timedelta_df: pd.DataFrame):
        pass
