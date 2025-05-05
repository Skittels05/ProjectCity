from json import dump, load
from pathlib import Path

class Config:
    config_loaded: dict[str]
    DOMAIN: str
    DATABASE_URL: str
    EMAIL: str
    EMAIL_PASSWORD: str

    def __init__(self):
        with open(Path(__file__).parent.parent / "config.json", 'r', encoding='utf-8') as file:
            self.config_loaded = load(file)
        self.DOMAIN = self.config_loaded.get("DOMAIN", None)
        self.DATABASE_URL = self.config_loaded.get("DATABASE_URL", None)
        self.EMAIL = self.config_loaded.get("EMAIL", None)
        self.EMAIL_PASSWORD = self.config_loaded.get("EMAIL_PASSWORD", None)

config_values = Config()

if config_values.DOMAIN is None:
    raise ValueError("В файле конфигурации не обнаружено домена!!!")
if config_values.DATABASE_URL is None:
    raise ValueError("В файле конфигурации не обнаружено ссылки на базу данных!!!")
if config_values.EMAIL is None:
    raise ValueError("В файле конфигурации не обнаружено Email!!!")
if config_values.EMAIL_PASSWORD is None:
    raise ValueError("В файле конфигурации не обнаружено пароля от Email!!!")

