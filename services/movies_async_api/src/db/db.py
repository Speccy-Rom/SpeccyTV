import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import DefaultDict, List, Optional, Type

from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as elastic_exceptions

from models.base import BaseGetAPIModel
from queryes.base import FilterInfo, PageInfo, ServiceQueryInfo, SortInfo


db_logger = logging.getLogger('DB')


class BaseDB(ABC):

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseGetAPIModel]:
        pass

    @property
    @abstractmethod
    def index(self) -> str:
        pass

    @property
    @abstractmethod
    def search_fields(self) -> Optional[dict]:
        pass

    @property
    @abstractmethod
    def sort_fields(self) -> Optional[dict]:
        pass

    @property
    @abstractmethod
    def filter_fields(self) -> Optional[list]:
        pass

    @abstractmethod
    async def get(self, item_id: str) -> Optional[BaseGetAPIModel]:
        pass

    @abstractmethod
    async def query_item(self, query: ServiceQueryInfo) -> List[BaseGetAPIModel]:
        pass


class ElasticDB(BaseDB):

    async def get(self, item_id: str) -> Optional[BaseGetAPIModel]:
        try:
            doc = await self.elastic.get(index=self.index, id=item_id)
            db_logger.info('Getting item %s in %s', item_id, self.index)
            return self.response_model(**doc['_source'])
        except elastic_exceptions.NotFoundError:
            db_logger.info('Item %s not found in %s', item_id, self.index)
            return None

    async def query_item(self, query: ServiceQueryInfo) -> List[BaseGetAPIModel]:
        body = self._elastic_request_for_query(query)
        doc = await self.elastic.search(index=self.index, body=body)
        db_logger.info('Searching in %s', self.index)
        return [self.response_model(**hit['_source']) for hit in doc['hits']['hits']]

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    def _elastic_pagination_request(self, page_info: PageInfo) -> DefaultDict[str, DefaultDict[str, dict]]:
        body = defaultdict(lambda: defaultdict(dict))
        body['from'] = page_info.number * page_info.size
        body['size'] = page_info.size
        body['query']['bool']['should'] = [{'match_all': {}}]
        body['query']['bool']['minimum_should_match'] = 1
        return body

    def _elastic_request_add_query(self, query: str, body: DefaultDict[str, DefaultDict[str, dict]]):
        if not query:
            return
        body['query']['bool']['should'] = []
        for field, weight in self.search_fields.items():
            match = defaultdict(lambda: defaultdict(dict))
            match['match'][field]['query'] = query
            match['match'][field]['fuzziness'] = 'auto'
            match['match'][field]['boost'] = weight
            body['query']['bool']['should'].append(match)

    def _elastic_request_add_filter(self, filter_request: FilterInfo, body: DefaultDict[str, DefaultDict[str, dict]]):
        if not filter_request:
            return
        body['query']['bool']['filter'] = []
        for field in self.filter_fields:
            uuid = filter_request.dict().get(field)
            if uuid is None:
                continue
            filter_info = defaultdict(lambda: defaultdict(dict))
            filter_info['nested']['path'] = field
            filter_info['nested']['query']['match'] = {f'{field}.id': str(uuid)}
            body['query']['bool']['filter'].append(filter_info)

    def _elastic_request_add_sort(self, sort_request: SortInfo, body: DefaultDict[str, DefaultDict[str, dict]]):
        if not sort_request:
            return
        body['sort'] = []
        sort = defaultdict(dict)
        elastic_sort_field = self.sort_fields.get(sort_request.field)
        sort[elastic_sort_field]['order'] = 'desc' if sort_request.desc else 'asc'
        body['sort'].append(sort)

    def _elastic_request_for_query(self, query_info: ServiceQueryInfo) -> dict:
        body = self._elastic_pagination_request(query_info.page)
        if query_info.query:
            self._elastic_request_add_query(query_info.query, body)
        if query_info.filter:
            self._elastic_request_add_filter(query_info.filter, body)
        if query_info.sort:
            self._elastic_request_add_sort(query_info.sort, body)

        return body
