from dependency_injector import resources
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker, DeclarativeMeta

PredictedBase = declarative_base()


class Predicted(PredictedBase):
    __tablename__ = "predicted"
    __tableargs__ = {
        "comment": "Рекомендуемые значения теплоносителя на выходе с котельной"
    }
    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    timestamp = Column(
        DateTime,
        comment="Дата и время"
    )
    forward_temp = Column(
        Float,
        comment="Температура на выходе из котельной"
    )
    circuit_type = Column(
        String,
        comment="Контур"
    )


class DBConnect(resources.Resource):
    _engine = None

    def init(self, path: str, base: DeclarativeMeta):
        self._engine = create_engine("sqlite:///" + path, echo=False)
        base.metadata.create_all(self._engine)
        session_factory = sessionmaker(bind=self._engine)
        return session_factory

    def shutdown(self) -> None:
        self._engine.dispose()
