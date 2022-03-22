from sqlalchemy import create_engine, MetaData, Table, or_

from data import config


engine = create_engine(config.URI)
meta = MetaData(engine)
cursor = engine.connect()
_users_db = Table('UsersInfo', meta, autoload=True)
_variants_db = Table('VariantsInfo', meta, autoload=True)


class DataBase:

    @property
    def cursor(self):
        return cursor


class UsersInfo(DataBase):

    def add_user(self, **kwargs):
        """
        Добавляет пользователя в БД
        :param user_id: telegram id (integer)
        :param name: fullname of user (string 255)
        :param timetable: his timetable as the dict. Example: {'0': datetime, '4': datetime, ...}
            key: it's a day of the week as number from 0 to 6, value: time as datetime object
        :param preparation_for: the name of what the student is preparing for. (string, default value: None)
            Examples: 'EGE', 'OGE'
        :param status: (string, default value: None)
        :param achievements: various achievements of the student as a dictionary with a key: the name of the
         achievement and the value: the number of times he received this achievement.
         Example: {'passed_the_EGE_variant_by_100_points': 2, 'passed_the_EGE_variant_by_90+_points': 13}
        :param curr_1: (integer, default value: 0)
        :param curr_2: (integer, default value: 0)
        :param reg_time: time when user was registered (datetime)
        :param requests: json
        :param notifications: json
        :param inventory: json
        """
        sql = _users_db.insert().values(**kwargs)
        self.cursor.execute(sql)

    def select_all_users(self):
        """Возвращает всех пользователей"""
        sql = _users_db.select()
        return self.cursor.execute(sql).fetchall()

    def select_user(self, user_id):
        """Возвращает пользователя с заданными параметрами **kwargs"""
        sql = _users_db.select().where(_users_db.c.user_id == user_id)
        return self.cursor.execute(sql).fetchone()

    def count_users(self):
        """Возвращает кол-во пользователей"""
        sql = _users_db.select()
        return len(self.cursor.execute(sql).fetchall())

    def update_data(self, user_id: int, **kwargs):
        """
        Обновляет данные change в таблице UsersInfo у пользователя user_id
        :param user_id: integer, telegram id
        :param kwargs: dictionary with arguments: (str: column_name, Any: new object in db)
        """
        sql = _users_db.update().where(_users_db.c.user_id == user_id).values(**kwargs)
        self.cursor.execute(sql)

    def delete_user(self, user_id):
        """Удаляет пользователя user_id из UsersInfo"""
        sql = _users_db.delete().where(_users_db.c.user_id == user_id)
        return self.cursor.execute(sql)


class VariantsInfo(DataBase):

    def add_variant(self, **kwargs):
        """Добавляет вариант в БД VariantsInfo
        title: str, answers: dict, type: str = None, status: str = None, source: str = None, additional: dict=None"""
        sql = _variants_db.insert().values(**kwargs)
        self.cursor.execute(sql)

    def select_all_variants(self):
        """Возвращает все варианты из БД VariantsInfo"""
        sql = _variants_db.select()
        return self.cursor.execute(sql).fetchall()

    def select_variant(self, variant_id=None, title=None):
        """Возвращает вариант с заданными параметрами"""
        if not variant_id and not title:
            raise ValueError('Должен быть передан хотя бы 1 аргумент variant_id или title')
        sql = _variants_db.select().where(
            or_(_variants_db.c.variant_id == variant_id, _variants_db.c.title == title))
        return self.cursor.execute(sql).fetchone()

    def count_variants(self):
        """Возвращает кол-во вариантов"""
        sql = _variants_db.select()
        return len(self.cursor.execute(sql).fetchall())

    def update_data(self, _variant_id: int = None, _title: str = None, **kwargs):
        """Обновляет данные в таблице VariantsInfo у варианта с заданным title или variant_id"""
        sql = _variants_db.update().where(
            or_(_variants_db.c.title == _title, _variants_db.c.variant_id == _variant_id)).values(**kwargs)
        self.cursor.execute(sql)

    def delete_variant(self, variant_id: int = None, title: str = None):
        """Удаляет вариант с заданным variant_id или title из VariantsInfo"""
        sql = _variants_db.delete().where(or_(_variants_db.c.variant_id == variant_id, _variants_db.c.title == title))
        return self.cursor.execute(sql)
