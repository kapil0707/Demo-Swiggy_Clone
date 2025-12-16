# This file contains configuration details to connect with database
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: str

    class Config:
        env_file = '.env'   

settings = Settings()