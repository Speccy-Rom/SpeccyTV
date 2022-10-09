from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class DBConfig(BaseSettings):
    postgres_db: str = Field("bitnami_airflow", env="POSTGRES_DB")
    postgres_host: str = Field("postgresql", env="POSTGRES_HOST")
    postgres_port: str = Field("5432", env="POSTGRES_PORT")
    postgres_user: str = Field("bn_airflow", env="POSTGRES_USER")
    postgres_password: str = Field("bitnami1", env="POSTGRES_PASSWORD")
    extract_query_location: str = Field("sql/extract.sql", env="EXTRACT_QUERY_LOCATION")
    load_query_location: str = Field("sql/insert.sql", env="LOAD_QUERY_LOCATION")

    class Config:
        env = ".env"


@lru_cache()
def get_converter_db_config():
    return DBConfig()
