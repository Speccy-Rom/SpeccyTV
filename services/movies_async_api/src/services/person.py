from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache import BaseCache, RedisCache
from db.db import BaseDB, ElasticDB
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    pass


class ElasticPersonDB(ElasticDB):
    response_model = Person
    index = 'persons'
    search_fields = {'name': 1.5}
    sort_fields = {'full_name': 'name.raw'}
    filter_fields = ['films']


def get_person_db(elastic: AsyncElasticsearch = Depends(get_elastic)) -> BaseDB:
    return ElasticPersonDB(elastic)


class RedisPersonCache(RedisCache):
    response_model = Person


def get_person_cache(redis: Redis = Depends(get_redis)) -> BaseCache:
    return RedisPersonCache(redis)


@lru_cache()
def get_person_service(cache: BaseCache = Depends(get_person_cache),
                       db: BaseDB = Depends(get_person_db)) -> PersonService:
    return PersonService(cache, db)
