from pydantic import BaseSettings
from pydantic.networks import PostgresDsn


class StripeSettings(BaseSettings):
    stripe_secret_key: str


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn = 'postgresql://postgres:postgres@localhost:5432/subscriptions'
    broker_url = 'pyamqp://guest:guest@localhost//'
    stripe_settings = StripeSettings()
    poll_timeout: int = 1


settings = Settings()
