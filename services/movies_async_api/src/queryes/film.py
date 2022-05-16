from uuid import UUID

from fastapi import Query

from core import config
from queryes.base import QueryParamsBase


class FilmQueryParamsInfo(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(imdb_rating|title)$',
                                   description='Field to sort by (imdb_rating, title)'),
                 filter_genre: UUID = Query(None, alias='filter[genre]', description='Filter by genre'),
                 filter_person: UUID = Query(None, alias='filter[person]', description='Filter by person')):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort, filter_genre=filter_genre,
                         filter_person=filter_person)


class FilmQueryParamsSearch(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(imdb_rating|title)$',
                                   description='Field to sort results by (imdb_rating, title). Default - by relevance'),
                 filter_genre: UUID = Query(None, alias='filter[genre]', description='Filter results by genre'),
                 filter_person: UUID = Query(None, alias='filter[person]', description='Filter results by person'),
                 query: str = Query(None, min_length=1, max_length=256,
                                    description='Search query (title and description fields will be inspected)')):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort, filter_genre=filter_genre,
                         filter_person=filter_person, query=query)
