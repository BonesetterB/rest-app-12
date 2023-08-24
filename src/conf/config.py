from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgres://kjewqvnk:AMUdWzrVvQFF42-KvvVyDWeLOVnV1eZ6@snuffleupagus.db.elephantsql.com/kjewqvnk"
    secret_key: str = "7fdd20f489c56745948db9e90d91f9d6a23abb28c1e87cb705fdc8b1bf0f1a3c"
    algorithm: str = "HS256"
    mail_username: str = "wulfich@meta.ua"
    mail_password: str ="0962565577Al"
    mail_from: str = "wulfich@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = "password"
    cloudinary_name: str ="cloudinary_name"
    cloudinary_api_key: str ="1234"
    cloudinary_api_secret: str="24354"

    model_config = ConfigDict(extra= 'ignore', env_file = ".env",env_file_encoding = "utf-8")



config = Settings()

