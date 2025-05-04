from json import dump, load
from pathlib import Path

class Config:
    config_loaded: dict[str]
    DATABASE_URL: str

    def __init__(self):
        with open(Path(__file__).parent.parent / "config.json", 'r', encoding='utf-8') as file:
            self.config_loaded = load(file)
        self.DATABASE_URL = self.config_loaded.get("DATABASE_URL", "None")

config_values = Config()
