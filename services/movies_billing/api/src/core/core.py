from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn = 'postgresql+asyncpg://postgres:postgres@localhost:5432/subscriptions'
    project_name = 'Billing API'
    debug = True
    test = False
    stripe_secret_key: str = 'key'

    jwt_secret_key: str = '123'
    jwt_algorithm: str = 'HS256'

    host: str = 'http://localhost:8000'
    success_callback: str = host + '/v1/subscription/success?session_id={CHECKOUT_SESSION_ID}'
    cancel_callback: str = host + '/v1/subscription/cancel'


settings = Settings()
