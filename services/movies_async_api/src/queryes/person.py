from uuid import UUID

from fastapi import Query

from core import config
from queryes.base import QueryParamsBase


class PersonQueryParamsInfo(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(full_name)$',
                                   description='Field to sort by full_name'),
                 filter_film: UUID = Query(None, alias='filter[film]', description='Filter by film'),
                 ):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort, filter_film=filter_film)


class PersonQueryParamsSearch(QueryParamsBase):
    def __init__(self,
                 page_number: int = Query(0, ge=0, alias='page[number]', description='Page number'),
                 page_size: int = Query(config.PAGE_SIZE, gt=0, alias='page[size]',
                                        description='Number of items per page'),
                 sort: str = Query(None, regex='^-?(full_name)$',
                                   description='Field to sort results by full_name. Default - by relevance'),
                 filter_film: UUID = Query(None, alias='filter[film]', description='Filter by film'),
                 query: str = Query(None, min_length=1, max_length=256,
                                    description='Search query (title and description fields will be inspected)')):
        super().__init__(page_number=page_number, page_size=page_size, sort=sort, filter_film=filter_film, query=query)
