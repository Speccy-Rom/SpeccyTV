import json
import logging
from pathlib import Path
from typing import Generator, List

import config
from elasticsearch import Elasticsearch, exceptions
from utils import backoff

module_logger = logging.getLogger('ElasticsearchLoader')


class ElasticsearchLoader:
    def __init__(self, hosts: list, chunk_size: int = config.ETL_CHUNK_SIZE):
        self.client = Elasticsearch(hosts=hosts)
        self.chunk_size = chunk_size

    def init(self, index_name: str):
        index_dir = Path(__file__).resolve(strict=True).parent.joinpath('indexes')
        file = index_dir.joinpath(f'{index_name}.json')
        with open(file, 'r') as index_file:
            data = json.load(index_file)
        try:
            self.client.indices.create(index=index_name, body=data)
        except exceptions.ElasticsearchException:
            module_logger.warning('Index already exist: %s', index_name)

    def load_to_es(self, records: List[dict], index_name: str) -> None:
        for prepared_query in self._get_chunk_query(records, index_name):
            str_query = '\n'.join(prepared_query) + '\n'
            self._post_to_es(str_query, index_name)
            module_logger.info('Post %d items to elastic search', len(prepared_query))

    @backoff(Exception, logger=module_logger)
    def _post_to_es(self, query: str, index: str) -> None:
        self.client.bulk(body=query, index=index)
        self.client.indices.refresh(index=index)

    def _get_chunk_query(self, rows: List[dict], index_name: str) -> Generator[List[str], None, None]:
        chunked_rows = (rows[i:i+self.chunk_size] for i in range(0, len(rows), self.chunk_size))

        for chunk in chunked_rows:
            prepared_query = []
            for row in chunk:
                prepared_query.extend([
                    json.dumps({'index': {'_index': index_name, '_id': row['id']}}),
                    json.dumps(row)
                ])
            yield prepared_query
