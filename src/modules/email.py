import aiosmtplib
from email.mime.text import MIMEText
from shutil import which

from pydantic.types import UUID
from .config import config_values
from .schemas import Issue

async def send_verification_email(email: str, token: str):
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
