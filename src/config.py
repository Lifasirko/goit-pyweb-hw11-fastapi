from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    # mail_from_name: str
    # mail_tls: bool
    # mail_ssl: bool

    secret_key: str
    algorithm: str
    # access_token_expire_minutes: int

    redis_host: str = 'localhost'
    redis_port: int = 6379

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    reset_password_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
