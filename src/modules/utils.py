from hashlib import sha256
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent

def get_password_hash(password: str) -> str:
    """Функция по получению хэша из пароля"""
    return sha256(password.encode()).hexdigest()

def verify_password(possible_password: str, hashed_password: str) -> bool:
    """Функция для проверки соответствия возможного пароля и хэша"""
    return sha256(possible_password.encode()).hexdigest() == hashed_password

def hash_sha256(arg) -> str:
    """Функция для получения хэша sha256"""
    return sha256(arg.encode()).hexdigest()

def print_logo():
    """Пишет красивую надпись в консоль"""
    print(
        """
    ______          _           _     _____ _ _            ___  ______ _____ 
    | ___ \\        (_)         | |   /  __ (_) |          / _ \\ | ___ \\_   _|
    | |_/ / __ ___  _  ___  ___| |_  | /  \\/_| |_ _   _  / /_\\ \\| |_/ / | |  
    |  __/ '__/ _ \\| |/ _ \\/ __| __| | |   | | __| | | | |  _  ||  __/  | |  
    | |  | | | (_) | |  __/ (__| |_  | \\__/\\ | |_| |_| | | | | || |    _| |_ 
    \\_|  |_|  \\___/| |\\___|\\___|\\__|  \\____/_|\\__|\\__, | \\_| |_/\\_|    \\___/ 
                  _/ |                             __/ |                     
                 |__/                             |___/                      
        """
    )

def get_api_doc(path: str) -> str:
    """Функция для получения документации из папки api_docs"""
    return (SCRIPT_DIR / path).read_text(encoding="UTF-8")
