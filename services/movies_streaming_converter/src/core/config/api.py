from functools import lru_cache

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    app_project_name: str = Field("convert_api", env="APP_PROJECT_NAME")

    class Config:
        env = ".env"


@lru_cache()
def get_config():
    return Config()
