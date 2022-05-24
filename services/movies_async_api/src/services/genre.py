from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache import BaseCache, RedisCache
from db.db import BaseDB, ElasticDB
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    pass


class ElasticGenreDB(ElasticDB):
    response_model = Genre
    index = 'genres'
    search_fields = {'name': 1.5, 'description': 1.0}
    sort_fields = {'name': 'name.raw'}
    filter_fields = []


def get_genre_db(elastic: AsyncElasticsearch = Depends(get_elastic)) -> BaseDB:
    return ElasticGenreDB(elastic)


class RedisGenreCache(RedisCache):
    response_model = Genre


def get_genre_cache(redis: Redis = Depends(get_redis)) -> BaseCache:
    return RedisGenreCache(redis)


@lru_cache()
def get_genre_service(cache: BaseCache = Depends(get_genre_cache),
                      db: BaseDB = Depends(get_genre_db)) -> GenreService:
    return GenreService(cache, db)
