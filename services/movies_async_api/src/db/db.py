import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import DefaultDict, List, Optional, Type

from elasticsearch import AsyncElasticsearch, exceptions as elastic_exceptions
from models.base import BaseGetAPIModel
from queryes.base import FilterInfo, PageInfo, ServiceQueryInfo, SortInfo

# Initialize a logger for database related logs
db_logger = logging.getLogger('DB')


class BaseDB(ABC):
    """
    Abstract base class for database. Defines the basic interface for a database.
    """

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseGetAPIModel]:
        """
        Abstract property that should return the model used for responses.
        """
        pass

    @property
    @abstractmethod
    def index(self) -> str:
        """
        Abstract property that should return the index used for the database.
        """
        pass

    @property
    @abstractmethod
    def search_fields(self) -> Optional[dict]:
        """
        Abstract property that should return the fields used for search in the database.
        """
        pass

    @property
    @abstractmethod
    def sort_fields(self) -> Optional[dict]:
        """
        Abstract property that should return the fields used for sorting in the database.
        """
        pass

    @property
    @abstractmethod
    def filter_fields(self) -> Optional[list]:
        """
        Abstract property that should return the fields used for filtering in the database.
        """
        pass

    @abstractmethod
    async def get(self, item_id: str) -> Optional[BaseGetAPIModel]:
        """
        Abstract method to get an item from the database.

        :param item_id: The id of the item to get.
        :return: The item from the database if found, else None.
        """
        pass

    @abstractmethod
    async def query_item(self, query: ServiceQueryInfo) -> List[BaseGetAPIModel]:
        """
        Abstract method to query items from the database.

        :param query: The query information.
        :return: The list of items from the database that match the query.
        """
        pass


class ElasticDB(BaseDB):
    """
    Implementation of the BaseDB abstract base class using Elasticsearch as the database.
    """

    def __init__(self, elastic: AsyncElasticsearch):
        """
        Initialize the ElasticDB with an Elasticsearch connection.

        :param elastic: The Elasticsearch connection to use.
        """
        self.elastic = elastic

    async def get(self, item_id: str) -> Optional[BaseGetAPIModel]:
        """
        Get an item from the Elasticsearch database.

        :param item_id: The id of the item to get.
        :return: The item from the database if found, else None.
        """
        try:
            doc = await self.elastic.get(index=self.index, id=item_id)
            db_logger.info('Getting item %s in %s', item_id, self.index)
            return self.response_model(**doc['_source'])
        except elastic_exceptions.NotFoundError:
            db_logger.info('Item %s not found in %s', item_id, self.index)
            return None

    async def query_item(self, query: ServiceQueryInfo) -> List[BaseGetAPIModel]:
        """
        Query items from the Elasticsearch database.

        :param query: The query information.
        :return: The list of items from the database that match the query.
        """
        body = self._elastic_request_for_query(query)
        doc = await self.elastic.search(index=self.index, body=body)
        db_logger.info('Searching in %s', self.index)
        return [self.response_model(**hit['_source']) for hit in doc['hits']['hits']]

    def _elastic_pagination_request(self, page_info: PageInfo) -> DefaultDict[str, DefaultDict[str, dict]]:
        """
        Prepare a pagination request for Elasticsearch.

        :param page_info: The pagination information.
        :return: The request body for Elasticsearch.
        """
        body = defaultdict(lambda: defaultdict(dict))
        body['from'] = page_info.number * page_info.size
        body['size'] = page_info.size
        body['query']['bool']['should'] = [{'match_all': {}}]
        body['query']['bool']['minimum_should_match'] = 1
        return body

    def _elastic_request_add_query(self, query: str, body: DefaultDict[str, DefaultDict[str, dict]]):
        """
        Add a query to the Elasticsearch request.

        :param query: The query string.
        :param body: The request body for Elasticsearch.
        """
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
        """
        Add a filter to the Elasticsearch request.

        :param filter_request: The filter information.
        :param body: The request body for Elasticsearch.
        """
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
        """
        Add a sort to the Elasticsearch request.

        :param sort_request: The sort information.
        :param body: The request body for Elasticsearch.
        """
        if not sort_request:
            return
        body['sort'] = []
        sort = defaultdict(dict)
        elastic_sort_field = self.sort_fields.get(sort_request.field)
        sort[elastic_sort_field]['order'] = 'desc' if sort_request.desc else 'asc'
        body['sort'].append(sort)

    def _elastic_request_for_query(self, query_info: ServiceQueryInfo) -> dict:
        """
        Prepare a query request for Elasticsearch.

        :param query_info: The query information.
        :return: The request body for Elasticsearch.
        """
        body = self._elastic_pagination_request(query_info.page)
        if query_info.query:
            self._elastic_request_add_query(query_info.query, body)
        if query_info.filter:
            self._elastic_request_add_filter(query_info.filter, body)
        if query_info.sort:
            self._elastic_request_add_sort(query_info.sort, body)

        return body
