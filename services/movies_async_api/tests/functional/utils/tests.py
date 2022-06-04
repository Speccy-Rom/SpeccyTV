import pytest


class TestAPIBase:
    @pytest.fixture(autouse=True)
    async def autoreset_cache(self, redis_client):
        await redis_client.flushall()
        