import logging
from typing import Generator, List, Union

import config
import psycopg2
from psycopg2.extras import DictCursor, DictRow
from .utils import backoff

# Setting up a logger for the module
module_logger = logging.getLogger('PostgresProducer')


class PostgresProducer:
    """
    A class used to represent a PostgreSQL Producer.

    ...

    Attributes
    ----------
    dsn : dict
        a dictionary containing the data source name (DSN) of the PostgreSQL database
    chunk_size : int
        the size of the chunks in which data is fetched from the database
    _connection : psycopg2.extensions.connection
        the connection to the PostgreSQL database
    _cursor : psycopg2.extensions.cursor
        the cursor object used to interact with the database

    Methods
    -------
    cursor():
        Initializes the cursor object.
    connect():
        Establishes a connection to the PostgreSQL database.
    execute(query: str, query_args: Union[List, str]) -> Generator[List[DictRow], None, None]:
        Executes a SQL query on the PostgreSQL database.
    reset():
        Resets the connection and cursor.
    close():
        Closes the connection to the PostgreSQL database.
    init():
        Initializes the connection and cursor.
    """

    def __init__(self, dsn: dict, chunk_size: int = config.ETL_CHUNK_SIZE):
        """
        Constructs all the necessary attributes for the PostgresProducer object.

        Parameters
        ----------
            dsn : dict
                a dictionary containing the data source name (DSN) of the PostgreSQL database
            chunk_size : int
                the size of the chunks in which data is fetched from the database
        """
        self.dsn = dsn
        self.chunk_size = chunk_size
        self._connection = None
        self._cursor = None

    def cursor(self) -> None:
        """
        Initializes the cursor object. If the cursor is closed or not yet initialized, a new cursor is created.
        """
        if not self._cursor or self._cursor.closed:
            if not self._connection:
                self.connect()
            self._cursor = self._connection.cursor(cursor_factory=DictCursor)

    @backoff(psycopg2.OperationalError, logger=module_logger)
    def connect(self) -> None:
        """
        Establishes a connection to the PostgreSQL database. If the connection is successful, autocommit is set to False.
        """
        self._connection = psycopg2.connect(**self.dsn)
        self._connection.autocommit = False
        module_logger.info('PostgreSQL connection is open')

    @backoff(exceptions=(psycopg2.DatabaseError, psycopg2.OperationalError), logger=module_logger)
    def execute(self, query: str, query_args: Union[List, str]) -> Generator[List[DictRow], None, None]:
        """
        Executes a SQL query on the PostgreSQL database. The query is executed in chunks of size chunk_size.

        Parameters
        ----------
            query : str
                the SQL query to be executed
            query_args : Union[List, str]
                the arguments to be passed to the SQL query

        Yields
        ------
            List[DictRow]
                a list of rows fetched from the database
        """
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
        """
        Resets the connection and cursor. The connection and cursor are closed and then reinitialized.
        """
        self.close()
        self.connect()
        self.cursor()

    def close(self) -> None:
        """
        Closes the connection to the PostgreSQL database. If the connection is open, the cursor and connection are closed.
        """
        if self._connection:
            if self._cursor:
                self._cursor.close()
            self._connection.close()
            module_logger.info('PostgreSQL connection is closed')
        self._connection = None
        self._cursor = None

    def init(self) -> None:
        """
        Initializes the connection and cursor. The connection and cursor are established.
        """
        self.connect()
        self.cursor()
