from pydantic import BaseSettings, Field


class PostgresSettings(BaseSettings):
    postgres_db: str = Field("convertations", env="POSTGRES_DB")
    postgres_host: str = Field("postgres", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field("convert", env="POSTGRES_USER")
    postgres_password: str = Field("convert", env="POSTGRES_PASSWORD")


def get_tortoise_config(postgres_settings: PostgresSettings = PostgresSettings()):
    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": postgres_settings.postgres_host,
                    "port": postgres_settings.postgres_port,
                    "database": postgres_settings.postgres_db,
                    "user": postgres_settings.postgres_user,
                    "password": postgres_settings.postgres_password,
                },
            }
        },
        "apps": {
            "models": {
                "models": ["db.postgres.models"],
                "default_connection": "default",
            },
        },
    }
