import os
from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


QUESTIONNAIRES_COMPILER_ENV_FILE_PATH = os.getenv(
    'QUESTIONNAIRES_COMPILER__ENV_FILE_PATH',
    '/run/configs/.env.questionnaires_compiler')
POSTGRES_ENV_FILE_PATH = os.getenv(
    'POSTGRES_ENV_FILE_PATH', '/run/envs/.env.postgres')
POSTGRES_CREDENTIALS_FILE_PATH = os.getenv(
    'POSTGRES_CREDENTIALS_FILE_PATH',
    '/secrets/questionnaires_compiler.credentials')
MONGO_ENV_FILE_PATH = ''
MONGO_CREDENTIALS_FILE_PATH =  ''

# TEST
# QUESTIONNAIRES_COMPILER__ENV_FILE_PATH = os.getenv(
#     'QUESTIONNAIRES_COMPILER__ENV_FILE_PATH', '../test/.test.env')
# POSTGRES_ENV_FILE_PATH = os.getenv(
#     'POSTGRES_ENV_FILE_PATH', '../test/.test.env')
# POSTGRES_CREDENTIALS_FILE_PATH = os.getenv(
#     'POSTGRES_CREDENTIALS_FILE_PATH', '../../database/secrets/questionnaires_compiler.credentials')

class EngineEnum(str, Enum):
    postgres = 'django.db.backends.postgresql'
    mysql = 'django.db.backends.mysql'


class DatabaseConfig(BaseSettings):
    DATABASE: str
    PASSWORD: str
    USER: str
    HOST: str
    PORT: int
    ENGINE: Optional[EngineEnum] = EngineEnum.postgres

    model_config = SettingsConfigDict(
        env_file=(POSTGRES_ENV_FILE_PATH, POSTGRES_CREDENTIALS_FILE_PATH),
        env_prefix='POSTGRES_',
        env_file_encoding='utf-8',
        secrets_dir='/secrets',
        extra='ignore'
    )


class MongoConfig(BaseSettings):
    DATABASE: str
    PASSWORD: str
    USER: str
    HOST: str
    PORT: int

    model_config = SettingsConfigDict(
        env_file=(MONGO_ENV_FILE_PATH, MONGO_CREDENTIALS_FILE_PATH),
        env_prefix='MONGO_',
        env_file_encoding='utf-8',
        secrets_dir='/secrets',
        extra='ignore'
    )


class ApplicationSettings(BaseSettings):

    WSGI_ON: bool
    JWT_SECRET: str

    WEBHOOK_ESTABLISHING_CONNECTION_TIMEOUT: int = 20
    WEBHOOK_RECEIVING_RESPONSE_TIMEOUT: int = 20

    model_config = SettingsConfigDict(
        env_file=(QUESTIONNAIRES_COMPILER_ENV_FILE_PATH,),
        env_file_encoding='utf-8',
        secrets_dir='/secrets',
        extra='ignore'
    )


class AdminSettings(BaseSettings):

    ADMIN_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=QUESTIONNAIRES_COMPILER_ENV_FILE_PATH,
        extra='ignore'
    )
