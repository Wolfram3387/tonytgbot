import json
import sqlite3
from time import time
from typing import Tuple, Any, Dict


class Database:
    def __init__(self, path_to_db='data/users.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(sql, parameters)

        connection.set_trace_callback(logger)

        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_users(self):
        """Создаёт таблицу UsersInfo"""
        sql = """
        CREATE TABLE UsersInfo (
        user_id int NOT NULL,
        name varchar(255) NOT NULL,
        timetable varchar,
        preparation_for varchar(63),
        status varchar(63) NOT NULL,
        achievements varchar,
        curr_1 int NOT NULL,
        curr_2 int NOT NULL,
        reg_time int NOT NULL,
        requests varchar,
        notifications varchar,
        PRIMARY KEY (user_id)
        );
        """
        self.execute(sql, commit=True)

    def add_user(self, user_id: int,
                 name: str,
                 timetable=None,    # : Dict[str: str]
                 preparation_for: str = None,
                 status='',
                 achievements=None,    # Dict[str: int]
                 curr_1: int = 0,
                 curr_2: int = 0,
                 reg_time: int = None,
                 requests: str = None,    # Dict
                 notifications: str = None):    # Dict
        """
        Добавляет пользователя в БД
        :param user_id: telegram id
        :param name: fullname of user
        :param timetable: his timetable as the dict. Example: {'tuesday': '16:45', 'friday': '18:30', ...}
            key: it's a day of the week, value: time as a str
        :param preparation_for: the name of what the student is preparing for. Examples: 'EGE', 'OGE'
        :param status:
        :param achievements: various achievements of the student as a dictionary with a key: the name of the
         achievement and the value: the number of times he received this achievement.
         Example: {'passed_the_EGE_variant_by_100_points': 2, 'passed_the_EGE_variant_by_90+_points': 13}
        :param curr_1: 0
        :param curr_2: 0
        :param reg_time: time when user was registered in seconds since early 1970
        """
        if not timetable:
            timetable = dict()
        if not achievements:
            achievements = dict()
        if not reg_time:
            reg_time = int(time())
        if not requests:
            requests = dict()
        if not notifications:
            notifications = dict()
        timetable = json.dumps(timetable, separators=(',', ':'))
        achievements = json.dumps(achievements, separators=(',', ':'))
        requests = json.dumps(requests, separators=(',', ':'))
        notifications = json.dumps(notifications, separators=(',', ':'))

        sql = "INSERT INTO UsersInfo(user_id, name, timetable, preparation_for, status, achievements, curr_1, curr_2, reg_time, requests, notifications) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        parameters = (user_id, name, timetable, preparation_for, status, achievements, curr_1, curr_2, reg_time, requests, notifications)
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_users(self):
        """Возвращает всех пользователей"""
        sql = "SELECT * FROM UsersInfo"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        """
        Добавляет параметры в команду sql
        :param parameters:
        :param sql: 'SELECT * FROM UsersInfo WHERE ' (example)
        """
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):
        """Возвращает пользователей с заданными параметрами **kwargs"""
        sql = "SELECT * FROM UsersInfo WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def count_users(self):
        """Возвращает кол-во пользователей"""
        return self.execute("SELECT COUNT(*) FROM UsersInfo;", fetchone=True)

    def update_data(self, user_id: int, change: Tuple[str, Any]):
        """
        Обновляет данные change в таблице UsersInfo у пользователя user_id
        :param user_id: integer, telegram id
        :param change: tuple with two arguments: (str: column_name, Any: new object in db)
        """
        # TODO Можно переделать так, чтобы передавались **kwargs
        sql = f"UPDATE UsersInfo SET {change[0]}=? WHERE user_id=?"
        return self.execute(sql, parameters=(change[1], user_id), commit=True)

    def delete_user(self, user_id):
        """Удаляет пользователя user_id из UsersInfo"""
        sql = "DELETE FROM UsersInfo WHERE user_id=?"
        parameters = (user_id, )
        return self.execute(sql, parameters=parameters, commit=True)


def logger(statement):
    print(f'{"="*50}\nExecuting:\n{statement}\n{"="*50}')


class VariantsInfo:
    def __init__(self, path_to_db='data/variants.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(sql, parameters)

        connection.set_trace_callback(logger)

        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_variants_table(self):
        """Создаёт таблицу VariantsInfo"""    # answers ---> Dict{number: List[correct_answers]}
        sql = """
            CREATE TABLE VariantsInfo (
            variant_id int NOT NULL,
            title varchar(127) NOT NULL,
            answers varchar NOT NULL,
            type varchar(127),
            status varchar(127),
            source varchar(255),
            additional varchar,
            PRIMARY KEY (variant_id, title)
            );
            """
        self.execute(sql, commit=True)

    def add_variant(self, title: str, answers: dict, type: str = None, status: str = None, source: str = None, additional: dict=None):
        """Добавляет вариант в БД VariantsInfo"""

        if not additional:
            additional = dict()
        additional = json.dumps(additional, separators=(',', ':'))
        answers = json.dumps(answers, separators=(',', ':'))
        try:
            variant_id = max(line[0] for line in self.select_all_variants()) + 1
        except ValueError:
            variant_id = 1
        sql = "INSERT INTO VariantsInfo(variant_id, title, answers, type, status, source, additional) VALUES (?, ?, ?, ?, ?, ?, ?)"
        parameters = (variant_id, title, answers, type, status, source, additional)
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_variants(self):
        """Возвращает все варианты из БД VariantsInfo"""
        sql = "SELECT * FROM VariantsInfo"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        """
        Добавляет параметры в команду sql
        :param parameters:
        :param sql: 'SELECT * FROM VariantsInfo WHERE ' (example)
        """
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_variant(self, variant_id=None, title=None):
        """Возвращает вариант с заданными параметрами"""
        if not variant_id and not title:
            raise ValueError('Должен быть передан хотя бы 1 аргумент variant_id или title')
        sql = "SELECT * FROM VariantsInfo WHERE variant_id=? OR title=?"
        parameters = (variant_id, title)
        return self.execute(sql, parameters, fetchone=True)

    def count_variants(self):
        """Возвращает кол-во вариантов"""
        return self.execute("SELECT COUNT(*) FROM VariantsInfo;", fetchone=True)

    def update_data(self, _variant_id: int = None, _title: str = None, **kwargs):
        """Обновляет данные в таблице VariantsInfo у варианта с заданным title или variant_id
        СТАРЫЕ ДАННЫЕ СТИРАЮТСЯ!"""
        assert len(kwargs) == 1    # Защита (тк можно изменить только 1 параметр)
        key, value = list(kwargs.keys())[0], list(kwargs.values())[0]
        sql = f"UPDATE VariantsInfo SET {key}=? WHERE title=? OR variant_id=?"
        return self.execute(sql, parameters=(value, _title, _variant_id), commit=True)

    def delete_variant(self, variant_id: int = None, title: str = None):
        """Удаляет вариант с заданным variant_id или title из VariantsInfo"""
        sql = "DELETE FROM VariantsInfo WHERE variant_id=? OR title=?"
        parameters = (variant_id, title)
        return self.execute(sql, parameters=parameters, commit=True)
