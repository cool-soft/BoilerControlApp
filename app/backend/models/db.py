from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import INTEGER, DATETIME, FLOAT

AppDBBase = declarative_base()


class WeatherForecast(AppDBBase):
    __tablename__ = "weather_forecast"
    record_id = Column(INTEGER, primary_key=True, autoincrement=True)
    timestamp = Column(DATETIME, unique=True, nullable=False)
    weather_temp = Column(FLOAT, nullable=False)
