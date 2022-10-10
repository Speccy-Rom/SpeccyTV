from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class ConverterAPIConfig(BaseSettings):
    convert_api_host: str = Field("http://api:8001", env="CONVERT_API_HOST")
    convert_directory_path: str = Field("./data/online-movies-storage/", env="CONVERT_DIRECTORY_PATH")
    codec_name: Optional[str] = Field(None, env="CODEC_NAME")
    display_aspect_ratio: Optional[str] = Field(None, env="DISPLAY_ASPECT_RATIO")
    fps: Optional[str] = Field(None, env="FPS")

    class Config:
        env = ".env"


@lru_cache()
def get_converter_API_config():
    return ConverterAPIConfig()
