from fastapi import Query

from core import config
from queryes.base import QueryParamsBase


class GenreQueryParamsInfo(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(name)$',
                                   description='Field to sort by name'),
                 ):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort)


class GenreQueryParamsSearch(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(name)$',
                                   description='Field to sort results by name. Default - by relevance'),
                 query: str = Query(None, min_length=1, max_length=256,
                                    description='Search query (title and description fields will be inspected)')):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort, query=query)
