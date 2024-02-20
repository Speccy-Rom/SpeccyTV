import pytest


class TestAPIBase:
    @pytest.fixture(autouse=True)
    async def autoreset_cache(self, redis_client):
        await redis_client.flushall()


class TestAPI(TestAPIBase):
    @pytest.mark.asyncio
    async def test_get(self, session, api_url):
        async with session.get(api_url) as resp:
            assert resp.status == 200
            assert await resp.text() == 'Hello, world!'

    @pytest.mark.asyncio
    async def test_post(self, session, api_url):
        async with session.post(api_url) as resp:
            assert resp.status == 200
            assert await resp.text() == 'Hello, world!'

    @pytest.mark.asyncio
    async def test_put(self, session, api_url):
        async with session.put(api_url) as resp:
            assert resp.status == 200
            assert await resp.text() == 'Hello, world!'

    @pytest.mark.asyncio
    async def test_delete(self, session, api_url):
        async with session.delete(api_url) as resp:
            assert resp.status == 200
            assert await resp.text() == 'Hello, world!'

    @pytest.mark.asyncio
    async def test_patch(self, session, api_url):
        async with session.patch(api_url) as resp:
            assert resp.status == 200
            assert await resp.text() == 'Hello, world!'
