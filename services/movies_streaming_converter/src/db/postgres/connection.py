from core.config.postgres import get_tortoise_config
from tortoise import Tortoise


async def init_postgres():
    await Tortoise.init(config=get_tortoise_config())
    await Tortoise.generate_schemas()


async def close_postgres():
    await Tortoise.close_connections()
    