from json import dump, load
from dotenv import load_dotenv
from pathlib import Path

import os

load_dotenv()

class Config:
    # config_loaded: dict[str]
    DOMAIN: str
    PORT: int
    SSL_KEYFILE: str
    SSL_CERTFILE: str
    DATABASE_URL: str
    REDIS_URL: str
    EMAIL_DOMAIN: str
    EMAIL_PORT: int
    EMAIL: str
    EMAIL_PASSWORD: str
    USE_TLS: bool

    def __init__(self):
        # Использование JSON
        # with open(Path(__file__).parent.parent / "config.json", 'r', encoding='utf-8') as file:
        #     self.config_loaded = load(file)
        # self.DOMAIN = self.config_loaded.get("DOMAIN", None)
        # self.PORT = self.config_loaded.get("PORT", None)
        # self.SSL_KEYFILE = self.config_loaded.get("SSL_KEYFILE", None)
        # self.SSL_CERTFILE = self.config_loaded.get("SSL_CERTFILE", None)
        # self.DATABASE_URL = self.config_loaded.get("DATABASE_URL", None)
        # self.REDIS_URL = self.config_loaded.get("REDIS_URL", None)
        # self.EMAIL_DOMAIN = self.config_loaded.get("EMAIL_DOMAIN", None)
        # self.EMAIL_PORT = self.config_loaded.get("EMAIL_PORT", None)
        # self.EMAIL = self.config_loaded.get("EMAIL", None)
        # self.EMAIL_PASSWORD = self.config_loaded.get("EMAIL_PASSWORD", None)

        # Использование среды
        self.DOMAIN = os.getenv("DOMAIN")
        self.PORT = int(os.getenv("PORT"))
        self.SSL_KEYFILE = os.getenv("SSL_KEYFILE")
        self.SSL_CERTFILE = os.getenv("SSL_CERTFILE")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN")
        self.EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
        self.EMAIL = os.getenv("EMAIL")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        if os.getenv("USE_TLS") == "True":
            self.USE_TLS = True
        else:
            self.USE_TLS = False
        self.correct_email = False

config_values = Config()

if config_values.DOMAIN is None:
    raise ValueError("В файле конфигурации не обнаружено домена!!!")
if config_values.PORT is None:
    raise ValueError("В файле конфигурации не обнаружено порта!!!")
if config_values.DATABASE_URL is None:
    raise ValueError("В файле конфигурации не обнаружено ссылки на базу данных!!!")
if config_values.REDIS_URL is None:
    raise ValueError("В файле конфигурации не обнаружено ссылки на БД для кэша (Redis)!!!")
if config_values.EMAIL_DOMAIN is None:
    raise ValueError("В файле конфигурации не обнаружено домена сервера email!!!")
if config_values.EMAIL_PORT is None:
    raise ValueError("В файле конфигурации не обнаружено порта сервера email!!!")
if config_values.EMAIL is None:
    raise ValueError("В файле конфигурации не обнаружено Email!!!")
if config_values.EMAIL_PASSWORD is None:
    raise ValueError("В файле конфигурации не обнаружено пароля от Email!!!")

