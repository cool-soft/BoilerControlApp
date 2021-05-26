import logging

import pandas as pd
from aiorwlock import RWLock
from boiler.constants import column_names, dataset_prototypes
from boiler.data_processing.beetween_filter_algorithm \
    import AbstractTimestampFilterAlgorithm, LeftClosedTimestampFilterAlgorithm


class WeatherForecastRepository:

    def __init__(self,
                 filter_algorithm: AbstractTimestampFilterAlgorithm = LeftClosedTimestampFilterAlgorithm(),
                 drop_filter_algorithm: AbstractTimestampFilterAlgorithm = LeftClosedTimestampFilterAlgorithm()
                 ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._rwlock = None
        self._storage: pd.DataFrame = dataset_prototypes.WEATHER.copy()
        self._filter_algorithm = filter_algorithm
        self._drop_filter_algorithm = drop_filter_algorithm

    def _get_rwlock(self):
        if self._rwlock is None:
            self._rwlock = RWLock()
        return self._rwlock

    async def get_weather_forecast_by_timestamp_range(self,
                                                      start_timestamp: pd.Timestamp,
                                                      end_timestamp: pd.Timestamp
                                                      ) -> pd.DataFrame:

        self._logger.debug(f"Requested weather forecast for timestamp range: "
                           f"{start_timestamp}: {end_timestamp}")
        async with self._get_rwlock().reader_lock:
            weather_forecast_df = \
                self._filter_algorithm.filter_df_by_min_max_timestamp(
                    self._storage,
                    start_timestamp,
                    end_timestamp
                )
        return weather_forecast_df

    async def set_weather_forecast(self, weather_df: pd.DataFrame) -> None:
        async with self._get_rwlock().writer_lock:
            self._storage = self._storage.append(weather_df)
            self._storage = self._storage.drop_duplicates(
                column_names.TIMESTAMP,
                keep="last",
                ignore_index=True
            )
            self._storage = self._storage.sort_values(by=column_names.TIMESTAMP, ignore_index=True)

    async def drop_weather_forecast_older_than(self, timestamp: pd.Timestamp) -> None:
        self._logger.debug(f"Requested deleting weather forecast older than {timestamp}")
        async with self._get_rwlock().writer_lock:
            self._storage = self._drop_filter_algorithm.filter_df_by_min_max_timestamp(
                self._storage,
                timestamp,
                None
            )
