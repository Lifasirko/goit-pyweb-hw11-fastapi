from pydantic import BaseSettings


class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_tls: bool
    mail_ssl: bool
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
