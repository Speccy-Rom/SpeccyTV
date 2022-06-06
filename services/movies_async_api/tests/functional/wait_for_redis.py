import asyncio
import logging
from logging import config as logging_config

import aioredis

from logger import LOGGER_CONFIG
from settings import REDIS_HOST, REDIS_PORT, REDIS_TEST_DB


logging_config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger('RedisWaiter')


async def connect_to_redis():
    redis_client = await aioredis.create_redis((REDIS_HOST, REDIS_PORT), db=REDIS_TEST_DB)
    ping = bytes()

    while not ping == b'PONG':
        await asyncio.sleep(1)
        ping = await redis_client.ping()

    redis_client.close()
    await redis_client.wait_closed()


async def main():
    try:
        await asyncio.wait_for(connect_to_redis(), timeout=100)
    except asyncio.TimeoutError:
        logger.error('Failed to connect redis!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
