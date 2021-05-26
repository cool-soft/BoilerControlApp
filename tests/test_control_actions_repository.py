from random import random

import pandas as pd
import pytest
from boiler.constants import dataset_prototypes, column_names, circuit_types
from boiler.data_processing.beetween_filter_algorithm import FullClosedTimestampFilterAlgorithm
from dateutil.tz import gettz

from backend.repositories.control_action_repository import ControlActionsRepository


class TestControlActionsRepository:
    time_tick = pd.Timedelta(seconds=300)
    start_timestamp = pd.Timestamp.now(tz=gettz("Asia/Yekaterinburg"))
    end_timestamp = start_timestamp + (20 * time_tick)
    drop_timestamp = start_timestamp + (10 * time_tick)

    @pytest.fixture
    def repository(self):
        return ControlActionsRepository(filter_algorithm=FullClosedTimestampFilterAlgorithm())

    @pytest.fixture
    def control_actions_df(self):
        actions_df = dataset_prototypes.CONTROL_ACTION.copy()

        current_timestamp = self.start_timestamp
        while current_timestamp < self.end_timestamp:
            actions_df = actions_df.append(
                {
                    column_names.TIMESTAMP: current_timestamp,
                    column_names.FORWARD_PIPE_COOLANT_TEMP: random(),
                    column_names.CIRCUIT_TYPE: circuit_types.HEATING
                },
                ignore_index=True
            )
            current_timestamp += self.time_tick

        return actions_df

    @pytest.mark.asyncio
    async def test_set_get(self, control_actions_df, repository):
        await repository.add_control_actions(control_actions_df)
        loaded_control_actions = await repository.get_control_actions_by_timestamp_range(
            self.start_timestamp,
            self.end_timestamp
        )
        assert control_actions_df.to_dict("records") == loaded_control_actions.to_dict("records")

    @pytest.mark.asyncio
    async def test_set_drop_get(self, control_actions_df, repository):
        await repository.add_control_actions(control_actions_df)
        await repository.drop_control_actions_older_than(self.drop_timestamp)
        loaded_control_actions = await repository.get_control_actions_by_timestamp_range(
            self.start_timestamp,
            self.end_timestamp
        )
        assert not loaded_control_actions.empty
        assert (control_actions_df.columns == loaded_control_actions.columns).all()
        assert loaded_control_actions[column_names.TIMESTAMP].min() >= self.drop_timestamp
