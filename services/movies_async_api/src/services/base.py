import logging
from abc import ABC
from typing import List, Optional, Union

import backoff
from elasticsearch import exceptions as elastic_exceptions

from core import config
from db.cache import BaseCache
from db.db import BaseDB
from models.film import Film
from models.genre import Genre
from models.person import Person
from queryes.base import ServiceQueryInfo

module_logger = logging.getLogger('Service')


class BaseService(ABC):

    def __init__(self, cache: BaseCache, db: BaseDB):
        self.cache = cache
        self.db = db

    def _prefixed_key(self, key, prefix=None):
        prefix = prefix or self.__class__.__name__
        return '{prefix}:{key}'.format(prefix=prefix, key=key)

    def _complete_prefixed_key(self, key, prefix=None):
        """Adds a prefix containing an info about service and a kind of data to a key.
        E.g. a key 1-30:039ab... can be transformed to FilmService:List:1-30:039ab...
        """
        complete_key = key
        if prefix:
            complete_key = self._prefixed_key(complete_key, prefix)  # e.g. List:1-30:039ab...
        complete_key = self._prefixed_key(complete_key)  # e.g.  FilmService:List:1-30:039ab...
        return complete_key

    @backoff.on_exception(backoff.expo,
                          (elastic_exceptions.ConnectionError,),
                          max_time=config.TIME_LIMIT)
    async def get_by_id(self, item_id: str) -> Optional[Union[Film, Genre, Person]]:
        key_prefix = 'Details'
        item = await self._item_from_cache(item_id, key_prefix)
        if not item:
            item = await self._get_from_db(item_id)
            if not item:
                return None
            await self._put_item_to_cache(item, item.id, key_prefix)

        return item

    @backoff.on_exception(backoff.expo,
                          (elastic_exceptions.ConnectionError,),
                          max_time=config.TIME_LIMIT)
    async def get_by_query(self, query_info: ServiceQueryInfo) -> Optional[List[Union[Film, Genre, Person]]]:
        key_prefix = 'Search' if query_info.query else 'List'
        items = await self._item_from_cache(query_info.as_key(), key_prefix)
        if not items:
            items = await self._query_item_from_db(query_info)
            if not items:
                return None
            await self._put_item_to_cache(items, query_info.as_key(), key_prefix)

        return items

    async def _query_item_from_db(self, query_info: ServiceQueryInfo) -> List[Union[Film, Genre, Person]]:
        return await self.db.query_item(query=query_info)

    async def _get_from_db(self, item_id: str) -> Optional[Union[Film, Genre, Person]]:
        return await self.db.get(item_id)

    async def _item_from_cache(self, key: str, prefix: str = None) -> Optional[Union[Union[Film, Genre, Person],
                                                                                     List[Union[Film, Genre, Person]]]]:
        cache_key = self._complete_prefixed_key(key, prefix)
        module_logger.info('Looking for item in cache (key %s)', cache_key)
        return await self.cache.get(cache_key)

    async def _put_item_to_cache(self, item: Union[Union[Film, Genre, Person], List[Union[Film, Genre, Person]]],
                                 key: str, prefix: str = None):
        cache_key = self._complete_prefixed_key(key, prefix)
        module_logger.info('Putting item to cache for key %s)', cache_key)
        await self.cache.set(item, cache_key)
