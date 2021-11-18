# from sqlalchemy import MetaData, Table, String, Integer, Column, Text, Boolean, create_engine, ForeignKey, ext
import random
from pprint import pprint
import sqlalchemy

from myVK import VK
import VKfinder


def create_tables():
    '''
    создаем таблицуы, если не существуют
    '''
    engine = sqlalchemy.create_engine('postgresql://vkfinder:pass@localhost:5432/vkfinder')
    connection = engine.connect()
    inspector = sqlalchemy.inspect(engine)

    if 'users' not in inspector.get_table_names():
        connection.execute('''
            CREATE TABLE users(
            id serial PRIMARY KEY,
            id_user INTEGER UNIQUE NOT NULL,
            sex INTEGER NOT NULL,
            age INTEGER NOT NULL,
            city INTEGER NOT NULL
            );
        ''')

    if 'blacklist' not in inspector.get_table_names():
        connection.execute('''
            CREATE TABLE blacklist(
            id serial PRIMARY KEY,
            id_user INTEGER NOT NULL REFERENCES users(id),
            id_found_user INTEGER NOT NULL
            );
        ''')


def add_user(id_user, sex, age, city):
    '''
    добавляем пользователя с параметрами в db
    :param id_user: id пользователя
    :param sex: пол
    :param age: год рождения
    :param city: город проживания
    '''
    engine = sqlalchemy.create_engine('postgresql://vkfinder:pass@localhost:5432/vkfinder')
    connection = engine.connect()
    if not search_id_user_in_users(id_user):
        connection.execute(f'INSERT INTO users(id_user, sex, age, city) VALUES({id_user}, {sex}, {age}, {city});')


def add_in_blacklist(id_user, id_found_user):
    '''
    добавляем пользователя в 'черный список'
    :param id_user: id пользователя для кого ищем
    :param id_found_user: id пользовтеля, которого нашли
    '''
    engine = sqlalchemy.create_engine('postgresql://vkfinder:pass@localhost:5432/vkfinder')
    connection = engine.connect()
    id = connection.execute(f"SELECT id FROM users WHERE id_user = {id_user};").fetchall()
    id = list(id[0])[0]
    connection.execute(f"INSERT INTO blacklist(id_user, id_found_user) VALUES({id}, {id_found_user});")


def search_id_user_in_users(id_user):
    '''
    проверяет, есть ли запрашиваемый пользователь в таблице 'users'
    :param id_user: id пользователя
    :return: True or False
    '''
    engine = sqlalchemy.create_engine('postgresql://vkfinder:pass@localhost:5432/vkfinder')
    connection = engine.connect()
    user = connection.execute(f'SELECT id_user FROM users WHERE id_user = {id_user};').fetchall()
    if user:
        return True
    else:
        return False


def search_id_user_in_blacklist(id_user, id_found):
    '''
    проверяет, есть ли запрашиваемый пользователь в таблице 'blacklist'
    :param id_user: id пользователя кого искали пару
    :param id_user: id пользователя которого нашли
    :return: True or False
    '''
    engine = sqlalchemy.create_engine('postgresql://vkfinder:pass@localhost:5432/vkfinder')
    connection = engine.connect()
    user = connection.execute(f'''
        SELECT users.id_user, blacklist.id_found_user FROM blacklist
        JOIN users ON users.id = blacklist.id_user
        WHERE users.id_user = {id_user} AND blacklist.id_found_user = {id_found};
        ''').fetchall()
    if user:
        return True
    else:
        return False


# if __name__ == '__main__':
#     main = VK(VKfinder.get_user_token())
#     id = main.screen_name_to_user_id('zilon')
#     print(VKfinder.get_user_data(2956123))
#     print(main.find_photos_in_vk(54546))
#     pass