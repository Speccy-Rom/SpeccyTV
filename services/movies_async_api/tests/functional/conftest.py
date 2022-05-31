import asyncio

import aiohttp
import aioredis
import aiofiles
import pytest
from elasticsearch import AsyncElasticsearch

from settings import (API_HOST, API_PORT, ELASTIC_HOST, ELASTIC_PORT,
                      REDIS_HOST, REDIS_PORT, REDIS_TEST_DB)
from utils.models import HTTPResponse


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=f'{ELASTIC_HOST}:{ELASTIC_PORT}')
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    redis_client = await aioredis.create_redis((REDIS_HOST, REDIS_PORT), db=REDIS_TEST_DB)
    yield redis_client
    redis_client.close()
    await redis_client.wait_closed()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def cleaner(es_client):
    async def inner(index):
        resp = await es_client.indices.delete(index=index)
        return resp

    return inner


@pytest.fixture(scope='module')
def tst_data(tst_data_path):
    with open(tst_data_path) as f:
        data = f.read()
    yield data


@pytest.fixture(scope='session')
def bulk_data_to_es(session, es_client):
    async def inner(data, index) -> HTTPResponse:
        url = f'http://{ELASTIC_HOST}:{ELASTIC_PORT}/{index}/_bulk'
        headers = {'Content-Type': 'application/json', 'charset': 'UTF-8'}

        async with session.post(url, data=data, headers=headers) as response:
            resp = HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
        await es_client.indices.refresh(index)
        return resp

    return inner


@pytest.fixture(scope='session')
def create_index(es_client):
    async def inner(index, index_schema_path):
        async with aiofiles.open(index_schema_path) as f:
            schema = await f.read()

        res = await es_client.indices.create(index=index, body=schema)
        await es_client.indices.refresh(index)
        return res

    return inner


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, endpoint_url: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = f'{endpoint_url}/{method}'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope='session')
def api_base_url():
    return f'http://{API_HOST}:{API_PORT}/api/v1'
