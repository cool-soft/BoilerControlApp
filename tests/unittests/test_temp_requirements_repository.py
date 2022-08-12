from datetime import datetime
from random import random, randint

import pandas as pd
import pytest
from boiler.constants import column_names, circuit_types, heating_object_types
from dateutil.tz import gettz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.models.db import TempRequirements
from backend.repositories.temp_requirements_reposiotry import TempRequirementsRepository


# noinspection PyMethodMayBeStatic
class TestTempRequirementsRepository:
    time_tick = pd.Timedelta(seconds=300)
    weather_data_timezone = gettz("Asia/Yekaterinburg")
    requirements_start_timestamp = datetime.now(tz=weather_data_timezone)
    requirements_end_timestamp = requirements_start_timestamp + (100 * time_tick)
    requirements_drop_timestamp = requirements_start_timestamp + (10 * time_tick)
    circuit_types = [circuit_types.HEATING, circuit_types.HOT_WATER]
    heating_obj_types = [heating_object_types.APARTMENT_HOUSE]

    db_url = "sqlite:///:memory:"

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            TempRequirements.metadata.drop_all(conn)
            TempRequirements.metadata.create_all(conn)
        db_session_maker = sessionmaker(
            autocommit=False,
            bind=engine
        )
        session_factory = scoped_session(
            db_session_maker
        )
        return session_factory

    @pytest.fixture
    def repository(self, session_factory):
        return TempRequirementsRepository(session_factory)

    @pytest.fixture
    def temp_requirements(self):
        requirements = {}
        for obj_type in self.heating_obj_types:
            requirements[obj_type] = {}
            for circuit_type in self.circuit_types:
                requirements_list = []
                current_timestamp = self.requirements_start_timestamp
                while current_timestamp < self.requirements_end_timestamp:
                    requirements_list.append({
                        column_names.TIMESTAMP: current_timestamp,
                        column_names.FORWARD_TEMP: random(),
                        column_names.BACKWARD_TEMP: random()
                    })
                    current_timestamp += self.time_tick
                requirements[obj_type][circuit_type] = pd.DataFrame(requirements_list)
        return requirements

    def test_set_get(self, temp_requirements, repository, session_factory):
        self._fill_repository(repository, session_factory, temp_requirements)

        for obj_type in temp_requirements.keys():
            for circuit_type in temp_requirements[obj_type].keys():
                with session_factory.begin():
                    loaded_temp_requirements = repository.get_temp_requirements(
                        obj_type,
                        circuit_type,
                        self.requirements_start_timestamp,
                        self.requirements_end_timestamp + self.time_tick
                    )
                assert loaded_temp_requirements.to_dict("records") == \
                       temp_requirements[obj_type][circuit_type].to_dict("records")

        session_factory.remove()

    def _fill_repository(self, repository, session_factory, temp_requirements):
        for obj_type in temp_requirements.keys():
            for circuit_type in temp_requirements[obj_type].keys():
                with session_factory.begin() as session:
                    repository.add_temp_requirements(
                        obj_type,
                        circuit_type,
                        temp_requirements[obj_type][circuit_type]
                    )
                    session.commit()

    def test_set_drop_get(self, temp_requirements, repository, session_factory):
        self._fill_repository(repository, session_factory, temp_requirements)

        with session_factory.begin() as session:
            repository.drop_temp_requirements_older_than(self.requirements_drop_timestamp)
            session.commit()
        session_factory.remove()
        for obj_type in temp_requirements.keys():
            for circuit_type in temp_requirements[obj_type].keys():
                with session_factory.begin():
                    loaded_temp_requirements = repository.get_temp_requirements(
                        obj_type,
                        circuit_type,
                        self.requirements_start_timestamp,
                        self.requirements_end_timestamp + self.time_tick
                    )
                assert not loaded_temp_requirements.empty
                assert (temp_requirements[obj_type][circuit_type].columns ==
                        loaded_temp_requirements.columns).all()
                assert loaded_temp_requirements[column_names.TIMESTAMP].min() >= self.requirements_drop_timestamp
        session_factory.remove()

    def test_set_with_update(self, temp_requirements, repository, session_factory):
        self._fill_repository(repository, session_factory, temp_requirements)

        obj_types = list(temp_requirements.keys())
        random_obj_type = obj_types[randint(0, len(obj_types)-1)]
        circuits = list(temp_requirements[random_obj_type].keys())
        random_circuit_type = circuits[randint(0, len(circuits)-1)]
        new_requirements_df = temp_requirements[random_obj_type][random_circuit_type].copy()

        index_count = len(new_requirements_df.index)
        for i in range(3):
            random_index = new_requirements_df.index[randint(0, index_count-1)]
            new_requirements_df.at[random_index, column_names.FORWARD_TEMP] = random()
            new_requirements_df.at[random_index, column_names.BACKWARD_TEMP] = random()
        with session_factory.begin() as session:
            repository.add_temp_requirements(random_obj_type, random_circuit_type, new_requirements_df)
            session.commit()

        with session_factory.begin():
            loaded_temp_requirements = repository.get_temp_requirements(
                random_obj_type,
                random_circuit_type,
                self.requirements_start_timestamp,
                self.requirements_end_timestamp + self.time_tick
            )

        session_factory.remove()
        assert new_requirements_df.to_dict("records") == loaded_temp_requirements.to_dict("records")

    def test_get_max_timestamp(self, temp_requirements, repository, session_factory):
        for obj_type in self.heating_obj_types:
            for circuit in self.circuit_types:
                with session_factory.begin():
                    max_cached_timestamp = repository.get_max_cached_timestamp(obj_type, circuit)
                    assert max_cached_timestamp is None

        self._fill_repository(repository, session_factory, temp_requirements)

        for obj_type in self.heating_obj_types:
            for circuit in self.circuit_types:
                with session_factory.begin():
                    max_cached_timestamp = repository.get_max_cached_timestamp(obj_type, circuit)
                    assert max_cached_timestamp == temp_requirements[obj_type][circuit][column_names.TIMESTAMP].max()

        session_factory.remove()
