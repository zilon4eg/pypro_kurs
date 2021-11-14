import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from pprint import pprint
import requests
from myVK import VK
import database


def write_msg(user_id, message, photos=None):
    if photos == None:
        vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7)})
    else:

        vk.method('messages.send', {'peer_id': user_id, 'message': message, 'attachment': photos, 'random_id': random.randrange(10 ** 7)})


def welcome_name(token, user_id, api_ver='5.81'):
    base_url = 'https://api.vk.com/method/'
    params = {
        'access_token': token,
        'user_id': user_id,
        'v': api_ver
    }
    firstname = requests.get(f'{base_url}users.get', params=params).json()
    return firstname['response'][0]['first_name']


def get_group_token():
    with open('vk_group_token.txt', "r") as file:
        for line in file:
            token = line
    return token


def get_user_token():
    with open('vk_standalone_token.txt', "r") as file:
        for line in file:
            token = line
    return token


def get_user_data(id_user):
    myVK = VK(get_user_token())
    vk_user = myVK.users_info(id_user)
    id = vk_user['response'][0]['id']
    sex = vk_user['response'][0]['sex']
    age = vk_user['response'][0]['bdate'][-4:]
    city = vk_user['response'][0]['city']['id']
    return [int(id), int(sex), int(age), int(city)]


def user_firstname(id_user):
    name = VK(get_user_token())
    try:
        firstname = name.users_info(id_user)['response'][0]['first_name']
    except:
        firstname = name.users_info(id_user)['response'][0]['screen_name']
    return firstname


def find_a_pair(main_user_id, user_parameters):
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
        elif 'error' in find.get_photos(id_user).keys():
            users.remove(id_user)
            print('УДАЛЕН закрытый профиль')
        else:
            return id_user


def get_photos(id_user):
    photo = VK(get_user_token())
    photos = photo.find_photos_in_vk(id_user)
    photos = list(f'photo{photo["owner_id"]}_{photo["id"]}' for photo in photos)
    photos = ','.join(photos)
    return str(photos)


if __name__ == '__main__':
    group_token = get_group_token()
    user_token = get_user_token()

    vk = vk_api.VkApi(token=group_token)
    longpoll = VkLongPoll(vk)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request in ['начать', 'привет']:
                    write_msg(event.user_id, f'Хай, {welcome_name(group_token, event.user_id)}!')
                elif request in ['найди мне пару', 'ищи', 'найди']:
                    print('<===============================>')
                    print(f'Для: {event.user_id}')
                    user_param = get_user_data(event.user_id)
                    database.add_user(user_param[0], user_param[1], user_param[2], user_param[3])
                    love_id = find_a_pair(event.user_id, user_param)
                    print(f'Нашли: {love_id}')
                    photos = get_photos(love_id)
                    # write_msg(event.user_id, f'Знакомься, это {user_firstname(love_id)} (https://vk.com/id{love_id})', photos)
                    write_msg(event.user_id, f'Знакомься, это {user_firstname(love_id)} (https://vk.com/id{love_id})', photos)
                    database.add_in_blacklist(event.user_id, love_id)
                    if request == 'нет':
                        database.add_in_blacklist(event.user_id, love_id)
                        write_msg(event.user_id, f'Не отчаивайся! Просто, попробуй еще разок)')
                    elif request == 'да':
                        write_msg(event.user_id, f'Поздравляю, дальше все в твоих руках!')

                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                else:
                    write_msg(event.user_id, "Не понял вашего ответа...")