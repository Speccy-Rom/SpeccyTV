import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

import orjson
import aioredis
from core import config
from models.base import BaseGetAPIModel

# Initialize a logger for cache related logs
cache_logger = logging.getLogger('Cache')


class BaseCache(ABC):
    """
    Abstract base class for cache. Defines the basic interface for a cache.
    """

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseGetAPIModel]:
        """
        Abstract property that should return the model used for responses.
        """
        pass

    @abstractmethod
    async def get(self, key: str, default=None) -> Optional[Union[BaseGetAPIModel, List[BaseGetAPIModel]]]:
        """
        Abstract method to get a value from the cache.

        :param key: The key to get the value for.
        :param default: The default value to return if the key is not found in the cache.
        :return: The value from the cache if the key is found, else the default value.
        """
        pass

    @abstractmethod
    async def set(self, item: Union[BaseGetAPIModel, List[BaseGetAPIModel]], key: str):
        """
        Abstract method to set a value in the cache.

        :param item: The value to set in the cache.
        :param key: The key to associate with the value.
        """
        pass


class RedisCache(BaseCache):
    """
    Implementation of the BaseCache abstract base class using Redis as the cache.
    """

    def __init__(self, redis: aioredis.Redis):
        """
        Initialize the RedisCache with a Redis connection.

        :param redis: The Redis connection to use.
        """
        self.redis = redis

    async def get(self, key: str, default=None) -> Optional[Union[BaseGetAPIModel, List[BaseGetAPIModel]]]:
        """
        Get a value from the Redis cache.

        :param key: The key to get the value for.
        :param default: The default value to return if the key is not found in the cache.
        :return: The value from the cache if the key is found, else the default value.
        """
        data = await self.redis.get(key)
        if not data:
            return default

        cache_logger.info('Cache hit (key %s)', key)
        data_obj = orjson.loads(data)
        if isinstance(data_obj, list):
            return [self.response_model.parse_obj(obj) for obj in data_obj]
        return self.response_model.parse_obj(data_obj)

    async def set(self, item: Union[BaseGetAPIModel, List[BaseGetAPIModel]], key: str):
        """
        Set a value in the Redis cache.

        :param item: The value to set in the cache.
        :param key: The key to associate with the value.
        """
        if isinstance(item, list):
            item_json_obj = [sub_item.dict() for sub_item in item]
        else:
            item_json_obj = item.dict()
        item_json = orjson.dumps(item_json_obj)
        await self.redis.set(key, item_json, expire=config.CACHE_EXPIRATION)

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
