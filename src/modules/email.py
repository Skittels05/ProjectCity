import smtplib
from email.mime.text import MIMEText
from .config import config_values

def send_verification_email(email: str, token: str):
    """Функция для отправки письма для подтверждения почты"""
    verification_url = f"https://{config_values.DOMAIN}/verify-email?token={token}"
    message = MIMEText(
        f"Для подтверждения email перейдите по ссылке: {verification_url}"
    )
    message["Subject"] = "Подтверждение регистрации"
    message["From"] = config_values.EMAIL  # f"noreply@{config_values.DOMAIN}"
    message["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(config_values.EMAIL, config_values.EMAIL_PASSWORD)
        server.send_message(message)
