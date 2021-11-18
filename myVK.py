import requests
from pprint import pprint
import json
import datetime

class VK:
    '''
    Класс для работы с api VK
    '''
    base_url = 'https://api.vk.com/method/'

    def __init__(self, token, api_ver='5.89'):
        self.params = {
            'access_token': token,
            'v': api_ver
        }

    def users_info(self, user_id):
        '''
        :param user_id: id пользователя
        :return: данные о пользователе
        '''
        params_user = {
            'user_id': user_id,
            'fields': 'bdate, sex, city, screen_name',
            'name_case': 'Nom'
        }
        users_info = requests.get(f'{self.base_url}users.get', params={**self.params, **params_user}).json()
        return users_info

    def search_users(self, sex, age, city):
        '''
        ищем пользователя по перечню параметров. отправляется 3 запроса с 3 разными статусами "семейного положения".
        :param sex: пол
        :param age: год рождения
        :param city: город проживания
        :return: список пользователей подходящих по параметрам
        '''
        status = [1, 5, 6]
        users_id_all = set()
        for item in status:
            params_user = {
                'offset': 0,
                'count': 1000,
                'city': city,
                'sex': sex,
                'status': item,
                'birth_year': age,
                'has_photo': 1
            }
            users = requests.get(f'{self.base_url}users.search', params={**self.params, **params_user}).json()
            users_id = set(id['id'] for id in users['response']['items'])
            users_id_all.update(users_id)
        return list(users_id_all)


    def screen_name_to_user_id(self, screen_name):
        '''
        преобразует 'screen name' в id.
        :param screen_name: screen name, идуще после https://vk.com/ в ссылке на страницу пользователя
        :return: id пользователя
        '''
        params_user = {
            'screen_name': screen_name
        }
        user_id = requests.get(f'{self.base_url}utils.resolveScreenName', params={**self.params, **params_user}).json()[
            'response']['object_id']
        return user_id

    def find_photos_in_vk(self, user_id, album_id='profile'):
        '''
        В соответствии с заданием, находит 3 фото либо возвращает список с 'error' внутри.
        :param user_id: id пользователя
        :param album_id: альбом в котором ищутся фотографии
        :return: список с 3 самыми залайкаными фото или ошибкой, если аккаунт закрыт
        '''
        params_photo = {
            'owner_id': int(user_id),
            'album_id': album_id,
            'extended': '1'
        }
        photos = requests.get(f'{self.base_url}photos.get', params={**self.params, **params_photo}).json()
        if 'error' in photos.keys():
            return list(msg for msg in photos.keys())
        else:
            photos = list({'owner_id': photo['owner_id'], 'id': photo['id'], 'likes': photo['likes']['count']} for photo in photos['response']['items'])
            photos = sorted(photos, key=lambda photo: photo['likes'], reverse=True)
            if len(photos) > 3:
                photos = [photos[0], photos[1], photos[2]]
            return photos

    def get_city_id(self, message):
        '''
        на основании ввода пользователя ищет город через api
        :param message: пользовательский ввод
        :return: id города
        '''
        params_city = {
            'country_id': 1,
            'q': message,
            'need_all': 0,
            'count': 100
        }
        cities = requests.get(f'{self.base_url}database.getCities', params={**self.params, **params_city}).json()
        cities = list({city['title']: city['id']} for city in cities["response"]["items"])

        if message.capitalize().strip() in cities:
            city = cities[message.capitalize().strip()]
            return city
        else:
            city = cities[0].values()
            city = [cc for cc in city][0]
            return city
