import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from pprint import pprint
import requests
from myVK import VK
import database


def write_msg(user_id, message, photos=None):
    '''
    отправка сообщения пользователю в чат
    :param user_id: id пользователя
    :param message: сообщение для пользователя
    :param photos: фотографии для пользователя
    '''
    if photos == None:
        vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7)})
    else:
        vk.method('messages.send', {'peer_id': user_id, 'message': message, 'attachment': photos, 'random_id': random.randrange(10 ** 7)})


def get_group_token():
    '''
    считываем токен группы из файла
    :return: токен группы
    '''
    with open('vk_group_token.txt', "r") as file:
        for line in file:
            token = line
    return token


def get_user_token():
    '''
    считываем токен пользователя из файла
    :return: токен пользователя
    '''
    with open('vk_standalone_token.txt', "r") as file:
        for line in file:
            token = line
    return token


def get_user_data(id_user):
    '''
    получаем параметры пользователя VK
    :param id_user: id пользователя
    :return: id, пол, год рождения, город проживания
    '''
    myVK = VK(get_user_token())
    vk_user = myVK.users_info(id_user)
    id = vk_user['response'][0]['id']
    sex = vk_user['response'][0]['sex']
    age = vk_user['response'][0]['bdate'][-4:]
    city = vk_user['response'][0]['city']['id']
    return [int(id), int(sex), int(age), int(city)]


def user_firstname(id_user):
    '''
    возвращает имя пользователя по id
    :param id_user: id пользователя
    :return: имя пользователя
    '''
    name = VK(get_user_token())
    try:
        firstname = name.users_info(id_user)['response'][0]['first_name']
    except:
        firstname = name.users_info(id_user)['response'][0]['screen_name']
    return firstname


def find_a_pair(main_user_id, user_parameters):
    '''
    побдирает пару по параметрам
    :param main_user_id: id пользователя, которому подбираем пару
    :param user_parameters: параметры по которым подбираем пару
    :return: id подобранного пользователя (пользователи из ЧС или с закрытым профилем отбрасываются)
    '''
    find = VK(get_user_token())
    find_param = user_parameters
    if find_param[1] == 1:
        find_param[1] = 2
    else:
        find_param[1] = 1
    users = find.search_users(user_parameters[1], user_parameters[2], user_parameters[3])
    count = len(users)
    for i in range(count):
        if not users:
            error = 'Не удалось найти пару'
            return error
        id_user = users[random.randint(0, len(users) - 1)]
        if database.search_id_user_in_blacklist(main_user_id, id_user):
            users.remove(id_user)
            print('УДАЛЕНА анкета из ЧС')
        elif 'error' in find.find_photos_in_vk(id_user):
            users.remove(id_user)
            print('УДАЛЕН закрытый профиль')
        else:
            return id_user


def get_photos(id_user):
    '''
    получаем фотографии и преобразуем их для запроса чрез vk_api
    :param id_user: id пользователя
    :return: фотографии в виде photo<owner.id>_<photo_id>
    '''
    photo = VK(get_user_token())
    photos = photo.find_photos_in_vk(id_user)
    photos = list(f'photo{photo["owner_id"]}_{photo["id"]}' for photo in photos)
    photos = ','.join(photos)
    return str(photos)


def yes_or_no():
    '''
    небольшое ветвление диалога
    '''
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower().strip()
                if request in ['нет', 'не похоже']:
                    database.add_in_blacklist(event.user_id, love_id)
                    write_msg(event.user_id, f'Не отчаивайся! Просто, попробуй еще разок)')
                    break
                elif request in ['да', 'похоже']:
                    write_msg(event.user_id, f'Поздравляю, дальше все в твоих руках!')
                    break


def sex_request_from_user():
    'запрос пола пользователя'
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_param[1] = event.text.lower().strip()
                break


def city_request_from_user():
    'запрос города проживания пользователя'
    find = VK(get_user_token())
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                message = event.text.lower().strip()
                user_param[3] = find.get_city_id(message)
                break


def bdate_request_from_user():
    'запрос года рождения пользователя'
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_param[2] = event.text.lower().strip()
                break


if __name__ == '__main__':
    group_token = get_group_token()
    user_token = get_user_token()
    vk = vk_api.VkApi(token=group_token)

    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower().strip()
                if request in ['начать', 'привет']:
                    write_msg(event.user_id, f'Хай, {user_firstname(event.user_id)}!')
                elif request in ['найди мне пару', 'ищи', 'найди']:
                    print('==================')
                    print(f'Для: {event.user_id}')
                    user_param = get_user_data(event.user_id)
                    if not user_param[1]:
                        write_msg(event.user_id, f'Похоже, в вашей анкете не указан пол. Вы мужчина или женщина?')
                        sex_request_from_user()
                    if not user_param[2]:
                        write_msg(event.user_id, f'Похоже, в вашей анкете не указан возраст. Какого вы года рождения?')
                        bdate_request_from_user()
                    if not user_param[3]:
                        write_msg(event.user_id, f'Похоже, в вашей анкете не указан город. Из какого вы города?')
                        city_request_from_user()
                    database.add_user(user_param[0], user_param[1], user_param[2], user_param[3])
                    love_id = find_a_pair(event.user_id, user_param)
                    print(f'Нашли: {love_id}')
                    photos = get_photos(love_id)
                    write_msg(event.user_id, f'Знакомься, это {user_firstname(love_id)} (https://vk.com/id{love_id})', photos)
                    write_msg(event.user_id, f'Похоже на твою половинку, как считаешь?')
                    yes_or_no()
                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                else:
                    write_msg(event.user_id, "Не понял вашего ответа...")
