import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

import orjson
from aioredis import Redis

from core import config
from models.base import BaseGetAPIModel


cache_logger = logging.getLogger('Cache')


class BaseCache(ABC):

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseGetAPIModel]:
        pass

    @abstractmethod
    async def get(self, key: str, default=None) -> Optional[Union[BaseGetAPIModel, List[BaseGetAPIModel]]]:
        pass

    @abstractmethod
    async def set(self, item: Union[BaseGetAPIModel, List[BaseGetAPIModel]], key: str):
        pass


class RedisCache(BaseCache):

    async def get(self, key: str, default=None) -> Optional[Union[BaseGetAPIModel, List[BaseGetAPIModel]]]:
        data = await self.redis.get(key)
        if not data:
            return default

        cache_logger.info('Cache hit (key %s)', key)
        data_obj = orjson.loads(data)
        if isinstance(data_obj, list):
            return [self.response_model.parse_obj(obj) for obj in data_obj]
        return self.response_model.parse_obj(data_obj)

    async def set(self, item: Union[BaseGetAPIModel, List[BaseGetAPIModel]], key: str):
        if isinstance(item, list):
            item_json_obj = [sub_item.dict() for sub_item in item]
        else:
            item_json_obj = item.dict()
        item_json = orjson.dumps(item_json_obj)
        await self.redis.set(key, item_json, expire=config.CACHE_EXPIRATION)

    def __init__(self, redis: Redis):
        self.redis = redis
