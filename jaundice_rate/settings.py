from pydantic import BaseSettings
from pydantic.fields import Field


class Settings(BaseSettings):
    """App settings."""

    fetch_timeout: int | float = Field(default=3, env='FETCH_TIMEOUT')
    url_limit: int = Field(default=10, env='URL_LIMIT')
    charged_words_directory: str = Field(default='jaundice_rate/charged_dict', env='CHARGED_WORDS_DIRECTORY')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
