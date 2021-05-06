from sqlalchemy import Column, TIMESTAMP, BIGINT, SMALLINT

from .base_model import BaseModel


class ControlAction(BaseModel):
    id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), unique=True)
    forward_temp = Column(SMALLINT())
