from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from core import config


class PageInfo(BaseModel):
    number: int = 0
    size: int = config.PAGE_SIZE


class FilterInfo(BaseModel):
    genre: Optional[UUID] = None
    person: Optional[UUID] = None
    films: Optional[UUID] = None


class SortInfo(BaseModel):
    field: str
    desc: bool


class ServiceQueryInfo(BaseModel):
    page: PageInfo = Field(default_factory=PageInfo)
    filter: Optional[FilterInfo] = None
    sort: Optional[SortInfo] = None
    query: Optional[str] = None

    def as_key(self):
        """
        Key for caching
        like: 1-50:039ab4ce-1497-45d7-9a6d-f153d82fb70a-None:imdb_rating-1:star
          or  10-20:None:imdb_rating-0:None
        """
        page_key = '{page_num}-{page_size}'.format(page_num=self.page.number, page_size=self.page.size)
        filter_key = '{genre}-{person}'.format(genre=self.filter.genre,
                                               person=self.filter.person) if self.filter else None
        sort_key = '{field}-{desc}'.format(field=self.sort.field,
                                           desc=int(self.sort.desc)) if self.sort else None
        query_key = self.query

        key = f'{page_key}:{filter_key}:{sort_key}:{query_key}'
        return key


class QueryParamsBase:
    def __init__(self,
                 page_number: int = 0,
                 page_size: int = config.PAGE_SIZE,
                 sort: str = None,
                 filter_genre: UUID = None,
                 filter_person: UUID = None,
                 filter_film: UUID = None,
                 query: str = None):
        self.query = query
        self.page = {'number': page_number,
                     'size': page_size}

        self.filter = None
        if filter_film or filter_genre or filter_person:
            self.filter = {'genre': filter_genre,
                           'person': filter_person,
                           'films': filter_film}

        self.sort = None
        if sort:
            self.sort = {'field': sort.removeprefix('-'),
                         'desc': sort.startswith('-')}

    def asdict(self):
        return {
                'page': self.page,
                'filter': self.filter,
                'sort': self.sort,
                'query': self.query
                }

    def __str__(self):
        return 'page: {page}, filter: {filter}, sort: {sort}, query: {query}'.format(page=self.page,
                                                                                     filter=self.filter,
                                                                                     sort=self.sort,
                                                                                     query=self.query)
    