import pandas as pd
from aiorwlock import RWLock
from boiler.constants import column_names, dataset_prototypes
from boiler.data_processing.beetween_filter_algorithm \
    import AbstractTimestampFilterAlgorithm, LeftClosedTimestampFilterAlgorithm

from backend.db.services import add_predicted_to_db
from backend.logger import logger


class ControlActionsRepository:

    def __init__(self,
                 filter_algorithm: AbstractTimestampFilterAlgorithm = LeftClosedTimestampFilterAlgorithm(),
                 drop_filter_algorithm: AbstractTimestampFilterAlgorithm = LeftClosedTimestampFilterAlgorithm()
                 ) -> None:
        self._rwlock = None
        self._storage: pd.DataFrame = dataset_prototypes.CONTROL_ACTION.copy()
        self._filter_algorithm = filter_algorithm
        self._drop_filter_algorithm = drop_filter_algorithm

        logger.debug(
            f"Creating instance:"
            f"filter_algorithm: {filter_algorithm}"
            f"drop_filter_algorithm: {drop_filter_algorithm}"
        )

    def _get_rwlock(self):
        if self._rwlock is None:
            self._rwlock = RWLock()
        return self._rwlock

    async def get_control_actions_by_timestamp_range(self,
                                                     start_timestamp: pd.Timestamp,
                                                     end_timestamp: pd.Timestamp
                                                     ) -> pd.DataFrame:

        logger.debug(
            f"Requested control actions for timestamp range: "
            f"{start_timestamp}: {end_timestamp}"
        )
        async with self._get_rwlock().reader_lock:
            control_actions_df = \
                self._filter_algorithm.filter_df_by_min_max_timestamp(
                    self._storage,
                    start_timestamp,
                    end_timestamp
                )
        return control_actions_df

    async def add_control_actions(self, control_actions_df: pd.DataFrame) -> None:
        logger.debug(f"Add the {len(control_actions_df)} control actions to repository")

        add_predicted_to_db(control_actions_df)

        async with self._get_rwlock().writer_lock:
            self._storage = self._storage.append(control_actions_df)
            self._storage = self._storage.drop_duplicates(
                column_names.TIMESTAMP,
                keep="last",
                ignore_index=True
            )
            self._storage = self._storage.sort_values(by=column_names.TIMESTAMP, ignore_index=True)

    async def drop_control_actions_older_than(self, timestamp: pd.Timestamp) -> None:
        logger.debug(f"Requested deleting control actions older than {timestamp}")
        async with self._get_rwlock().writer_lock:
            self._storage = self._drop_filter_algorithm.filter_df_by_min_max_timestamp(
                self._storage,
                timestamp,
                None
            )
