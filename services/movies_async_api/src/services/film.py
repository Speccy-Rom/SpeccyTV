from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache import BaseCache, RedisCache
from db.db import BaseDB, ElasticDB
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base import BaseService


class FilmService(BaseService):
    pass


class ElasticFilmDB(ElasticDB):
    response_model = Film
    index = 'movies'
    search_fields = {'title': 1.5, 'description': 1.0}
    sort_fields = {'imdb_rating': 'rating', 'title': 'title.raw'}
    filter_fields = ['genre', 'person']


def get_film_db(elastic: AsyncElasticsearch = Depends(get_elastic)) -> BaseDB:
    return ElasticFilmDB(elastic)


class RedisFilmCache(RedisCache):
    response_model = Film


def get_film_cache(redis: Redis = Depends(get_redis)) -> BaseCache:
    return RedisFilmCache(redis)


@lru_cache()
def get_film_service(cache: BaseCache = Depends(get_film_cache),
                     db: BaseDB = Depends(get_film_db)) -> FilmService:
    return FilmService(cache, db)
