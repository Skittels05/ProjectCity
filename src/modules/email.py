import aiosmtplib
import smtplib
from email.mime.text import MIMEText


from pydantic.types import UUID
from .config import config_values
from .schemas import Issue

def smtp_check(host: str, port: int, email: str, use_tls: bool = True, auth: bool = None) -> bool:
    try:
        with smtplib.SMTP(host, port, timeout=0.5) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            if auth:
                server.login(config_values.EMAIL, config_values.EMAIL_PASSWORD)
            message = MIMEText("Это тестовое письмо, которое возникает при запуске API. Проверка работоспособности SMTP сервера.", 'plain', 'utf-8')
            message["Subject"] = "SMTP Health Check"
            message["From"] = email
            message["To"] = email
            server.send_message(message)
            print("SMTP сервер работает корректно")
            return True
    except Exception as e:
        print(f"SMTP подключение прервано: {str(e)}")
        return False

async def send_verification_email(email: str, token: str) -> None:
    """Функция для отправки письма для подтверждения почты"""
    verification_url = f"https://{config_values.DOMAIN}/api/v1/user/verify-email?token={token}"
    message = MIMEText(
        f"Для подтверждения email перейдите по ссылке: {verification_url}",
        'plain',
        'utf-8'
    )
    message["Subject"] = "Подтверждение регистрации"
    message["From"] = config_values.EMAIL
    message["To"] = email
    async with aiosmtplib.SMTP(
        hostname=config_values.EMAIL_DOMAIN,
        port=config_values.EMAIL_PORT
    ) as server:
        await server.login(config_values.EMAIL, config_values.EMAIL_PASSWORD)
        await server.send_message(message)

async def send_notification_status(email: str, issue: Issue):
    """Отправка уведомления об изменении статуса проблемы"""
    message = MIMEText(
        f'Статус проблемы "{issue.type}" по адресу {issue.address} изменён на {issue.status}',
        'plain',
        'utf-8'
    )
    message["Subject"] = "Изменён статус вашей проблемы"
    message["From"] = config_values.EMAIL
    message["To"] = email
    async with aiosmtplib.SMTP(
        hostname=config_values.EMAIL_DOMAIN,
        port=config_values.EMAIL_PORT
    ) as server:
        await server.login(config_values.EMAIL, config_values.EMAIL_PASSWORD)
        await server.send_message(message)

async def reset_password_message(email: str, verify_token: UUID):
    """Отправка письма о сбросе пароля"""
    message = MIMEText(
        f'Отправлен запрос на сброс пароля, если это были вы, то перейдите по ссылке: '
        f'https://{config_values.DOMAIN}/api/v1/user/reset-password?token={verify_token}',
        'plain',
        'utf-8'
    )
    message["Subject"] = "Сброс пароля"
    message["From"] = config_values.EMAIL
    message["To"] = email
    async with aiosmtplib.SMTP(
        hostname=config_values.EMAIL_DOMAIN,
        port=config_values.EMAIL_PORT
    ) as server:
        await server.login(config_values.EMAIL, config_values.EMAIL_PASSWORD)
        await server.send_message(message)
    return 200
