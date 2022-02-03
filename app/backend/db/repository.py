from backend.db.resources import Predicted
from backend.db.schemas import PredictedData

from datetime import datetime


class DBRepository:

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def clear_table(self, table) -> None:
        """
        Очистка всей таблицы
        :param table: таблица
        :return: None
        """
        with self.session_factory() as session:
            rows = self.get_all(table)
            for row in rows:
                session.delete(row)
            session.commit()

    def get_all(self, table):
        """
        Возвращает содержимое всей таблицы
        :param table: таблица
        :return: все строки таблицы
        """
        with self.session_factory() as session:
            rows = session.query(table).all()
        return rows

    def get_from_period(self, table, column, start: datetime, end: datetime):
        """
        Возвращает содержимое таблицы за заданный период
        :param table: таблица
        :param column: колонка по которой будет выборка по времени
        :param start: начало временного интервала
        :param end: конец временного интервала
        :return: строки таблицы
        """
        with self.session_factory() as session:
            rows = session.query(table) \
                .filter(column >= start).filter(column <= end) \
                .all()
        return rows

    def add_predicted(self, data: PredictedData) -> None:
        """
        Добавление данных по рекомендуемым значения температуры теплоноситлея с бойлера в БД
        :param data: добавляемые данные
        :return:
        """
        with self.session_factory() as session:
            session.add(Predicted(timestamp=data.timestamp,
                                  forward_temp=data.forward_temp,
                                  circuit_type=data.circuit_type
                                  ))
            session.commit()

    def is_predicted(self, d_timestamp: datetime) -> bool:
        """
        Проверка существования в БД записи по погоде
        :param d_timestamp: дата и время снятия показаний
        :return: True - запись существует, False - запись не найдена
        """
        with self.session_factory() as session:
            data = session.query(Predicted) \
                .filter(Predicted.timestamp == d_timestamp) \
                .all()
        return len(data) > 0
