import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film, genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(title=config.PROJECT_NAME,
              description='Info about movies, genres and corresponding persons (e.g. actors, directors and writers)',
              docs_url='/api/openapi',
              openapi_url='/api/openapi.json',
              default_response_class=ORJSONResponse)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=['{host}:{port}'.format(host=config.ELASTIC_HOST, port=config.ELASTIC_PORT)])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(film.router, prefix='/api/v1/film', tags=['film'])
app.include_router(genre.router, prefix='/api/v1/genre', tags=['genre'])
app.include_router(person.router, prefix='/api/v1/person', tags=['person'])


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_config=LOGGING, log_level=logging.DEBUG, debug=True)
