import logging
from typing import Generator, List, Union

import config
import psycopg2
from psycopg2.extras import DictCursor, DictRow
from .utils import backoff

module_logger = logging.getLogger('PostgresProducer')


class PostgresProducer:
    def __init__(self, dsn: dict, chunk_size: int = config.ETL_CHUNK_SIZE):
        self.dsn = dsn
        self.chunk_size = chunk_size
        self._connection = None
        self._cursor = None

    def cursor(self) -> None:
        if not self._cursor or self._cursor.closed:
            if not self._connection:
                self.connect()
            self._cursor = self._connection.cursor(cursor_factory=DictCursor)

    @backoff(psycopg2.OperationalError, logger=module_logger)
    def connect(self) -> None:
        self._connection = psycopg2.connect(**self.dsn)
        self._connection.autocommit = False
        module_logger.info('PostgreSQL connection is open')

    @backoff(exceptions=(psycopg2.DatabaseError, psycopg2.OperationalError), logger=module_logger)
    def execute(self, query: str, query_args: Union[List, str]) -> Generator[List[DictRow], None, None]:
        try:
            if isinstance(query_args, str):
                query = self._cursor.mogrify(query, (query_args,))
            elif isinstance(query_args, list):
                query = self._cursor.mogrify(query, (tuple(query_args),))
            else:
                raise TypeError(f'Type of query args must be string or list. not {type(query_args)}')
            self._cursor.execute(query)
        except psycopg2.OperationalError:
            self.reset()
            raise
        else:
            while rows := self._cursor.fetchmany(self.chunk_size):
                yield rows

    def reset(self) -> None:
        self.close()
        self.connect()
        self.cursor()

    def close(self) -> None:
        if self._connection:
            if self._cursor:
                self._cursor.close()
            self._connection.close()
            module_logger.info('PostgreSQL connection is closed')
        self._connection = None
        self._cursor = None

    def init(self) -> None:
        self.connect()
        self.cursor()
