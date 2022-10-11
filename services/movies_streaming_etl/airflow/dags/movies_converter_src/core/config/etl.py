from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    prod_mode: bool = Field(False, env="PROD_MODE")
    schedule_interval: str = Field("00 12 * * *", env="SCHEDULE_INTERVAL")
    resolutions: List[int] = Field([1080, 720, 480, 360, 240, 120], env="RESOLUTIONS")

    class Config:
        env = ".env"


@lru_cache()
def get_config():
    return Config()
