import string
import random
import json
import requests
import datetime

USERS = 100
PASSWORD_LEN = 16
USERNAME_MIN_LEN = 6
USERNAME_MAX_LEN = 12
REG_URL = "http://localhost:8000/api/v1/user/register"

users = []

CHARS = string.ascii_letters + string.digits
EMAILS = ["@gmail.com", "@mail.ru", "@yandex.by", "@yandex.ru", "@example.com"]

SOGL = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "z", "p", "q", "r", "s", "t", "v", "w", "x", "y", "ch", "sh"]
GLAS = ["a", "e", "i", "o", "u", "y"]

def random_password():
    """Возвращает рандомный пароль"""
    password = ''
    for _ in range(PASSWORD_LEN):
        password += random.choice(CHARS + ".$#-_=+")
    return password

def random_username() -> str:
    """Возвращает рандомный никнейм"""
    o = bool(random.randint(0, 1))
    k = 0
    word = []
    for i in range(random.randint(5, 12)):
        if o == 0:
            word.append(random.choice(SOGL))
            if 50 <= random.randint(0, 100) <= 60:
                word.append(random.choice(SOGL))
            o = 1
        else:
            word.append(random.choice(GLAS))
            o = 0
    word_str = ''
    word_ram = ''.join(word)
    return word_ram

if __name__ == "__main__":
    base_start_time = datetime.datetime.now()
    for _ in range(USERS):
        users.append(
            {
                "username": random_username(),
                "email": random_username() + random.choice(EMAILS),
                "password": random_password()
            }
        )
    with open("users.json", 'w', encoding="UTF-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)

    # Блок регистрации
    for index, user in enumerate(users):
        start_time = datetime.datetime.now()
        print(f"Регистрацию проходит пользователь {index + 1}")
        req = requests.post(REG_URL, json=user)
        end_time = datetime.datetime.now()
        print(req.ok, '|', end_time - start_time, '|', req.text)
    base_end_time = datetime.datetime.now()
    print(f"На регистрацию было затрачено: {base_end_time - base_start_time}")
