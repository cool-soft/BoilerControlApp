from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import INTEGER, DATETIME, FLOAT, VARCHAR

AppDBBase = declarative_base()


class WeatherForecast(AppDBBase):
    __tablename__ = "weather_forecast"
    record_id = Column(INTEGER, primary_key=True, autoincrement=True)
    timestamp = Column(DATETIME, unique=True, nullable=False)
    weather_temp = Column(FLOAT, nullable=False)


class ControlAction(AppDBBase):
    __tablename__ = "control_action"
    record_id = Column(INTEGER, primary_key=True, autoincrement=True)
    timestamp = Column(DATETIME, nullable=False)
    circuit_type = Column(VARCHAR(32), nullable=False)
    forward_temp = Column(FLOAT, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'timestamp',
            'circuit_type',
            name='uq_timestamp_circuit_type'
        ),
    )


class TempGraph(AppDBBase):
    __tablename__ = "temp_graph"
    record_id = Column(INTEGER, primary_key=True, autoincrement=True)
    circuit_type = Column(VARCHAR(32), nullable=False)
    weather_temp = Column(FLOAT, nullable=False, unique=True)
    forward_temp = Column(FLOAT, nullable=False)
    backward_temp = Column(FLOAT, nullable=False)


class TempRequirements(AppDBBase):
    __tablename__ = "temp_requirements"
    record_id = Column(INTEGER, primary_key=True, autoincrement=True)
    timestamp = Column(DATETIME, nullable=False)
    circuit_type = Column(VARCHAR(32), nullable=False)
    heating_obj_type = Column(VARCHAR(32), nullable=False)
    forward_temp = Column(FLOAT, nullable=False)
    backward_temp = Column(FLOAT, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'timestamp',
            'circuit_type',
            'heating_obj_type',
            name='uq_timestamp_circuit_type_heating_obj_type'
        ),
    )
