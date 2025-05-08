from hashlib import sha256

def get_password_hash(password: str) -> str:
    """Функция по получению хэша из пароля"""
    return sha256(password.encode()).hexdigest()

def verify_password(possible_password: str, hashed_password: str) -> bool:
    """Функция для проверки соответствия возможного пароля и хэша"""
    return sha256(possible_password.encode()).hexdigest() == hashed_password
