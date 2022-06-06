import asyncio
import logging
from logging import config as logging_config

from elasticsearch import AsyncElasticsearch

from logger import LOGGER_CONFIG
from settings import ELASTIC_HOST, ELASTIC_PORT


logging_config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger('ESWaiter')


async def connect_to_es():
    es_client = AsyncElasticsearch(hosts='{host}:{port}'.format(host=ELASTIC_HOST, port=ELASTIC_PORT))
    ping = False

    while not ping:
        await asyncio.sleep(1)
        ping = await es_client.ping()

    await es_client.close()


async def main():
    try:
        await asyncio.wait_for(connect_to_es(), timeout=100)
    except asyncio.TimeoutError:
        logger.error('Failed to connect elastic!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
