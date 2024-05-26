from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from pathlib import Path

from src.config import settings
from src.services.auth import auth_service
from fastapi import BackgroundTasks
import os
from environs import Env

env = Env()
env.read_env()


conf = ConnectionConfig(
    MAIL_USERNAME=env.str('MAIL_USERNAME'),
    MAIL_PASSWORD=env.str('MAIL_PASSWORD'),
    MAIL_FROM=(env.str('MAIL_FROM')),
    MAIL_PORT=env.str('MAIL_PORT'),
    MAIL_SERVER=env.str('MAIL_SERVER'),
    MAIL_FROM_NAME="Rest API Application",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="example_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: str, reset_url: str):
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"To reset your password, visit the following link: {reset_url}",
        subtype="html"
    )
    fm = FastMail(settings.email_config)
    await fm.send_message(message)
